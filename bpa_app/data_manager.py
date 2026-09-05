"""
DATA MANAGER MODULE
Handles all data storage, retrieval, and metadata management
"""

import pandas as pd
import numpy as np
import json
import os
import shutil
from datetime import datetime
import hashlib
from typing import Dict, List, Optional, Any
import streamlit as st

class DataManager:
    """
    Manages all data operations for the bioprocess analyzer
    """
    
    def __init__(self, base_path: str = "./data"):
        self.base_path = base_path
        self.metadata_path = os.path.join(base_path, "metadata")
        self.raw_path = os.path.join(base_path, "raw")
        self.processed_path = os.path.join(base_path, "processed")
        self.comparisons_path = os.path.join(base_path, "comparisons")
        self.reports_path = os.path.join(base_path, "reports")
        
        # Ensure all directories exist
        self._create_directories()
    
    def _create_directories(self):
        """Create all necessary directories if they don't exist"""
        directories = [
            self.raw_path, self.processed_path, self.comparisons_path,
            self.reports_path, self.metadata_path,
            os.path.join(self.processed_path, "kinetics_results"),
            os.path.join(self.processed_path, "phase_detection"),
            os.path.join(self.processed_path, "yields")
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def save_raw_file(self, file, run_metadata: Dict) -> Dict:
        """
        Save uploaded raw file with metadata
        
        Parameters:
        - file: Uploaded file object from Streamlit
        - run_metadata: Dictionary with run information
        
        Returns:
        - Dictionary with saved file information
        """
        # Generate unique run ID
        run_id = self._generate_run_id(run_metadata)
        
        # Create year/month folder structure
        now = datetime.now()
        year_folder = now.strftime("%Y")
        month_folder = now.strftime("%m_%B")
        
        # Create folder path
        folder_path = os.path.join(self.raw_path, year_folder, month_folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Save file
        file_extension = file.name.split('.')[-1]
        filename = f"{run_id}.{file_extension}"
        file_path = os.path.join(folder_path, filename)
        
        # Read and save dataframe — accept file-like objects or wrapped DataFrames
        if hasattr(file, '_df') and isinstance(file._df, pd.DataFrame):
            df = file._df
        elif isinstance(file, pd.DataFrame):
            df = file
        else:
            df = pd.read_csv(file) if file_extension == 'csv' else pd.read_excel(file)
        df.to_csv(file_path, index=False)
        
        # Save metadata
        metadata = {
            'run_id': run_id,
            'original_filename': file.name,
            'saved_filename': filename,
            'saved_path': file_path,
            'upload_date': now.isoformat(),
            'file_size_kb': os.path.getsize(file_path) / 1024,
            'rows': len(df),
            'columns': list(df.columns),
            **run_metadata
        }
        
        # Save metadata as JSON
        metadata_path = os.path.join(self.metadata_path, f"{run_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        # Update runs database
        self._update_runs_database(metadata)
        
        return metadata
    
    def save_kinetics_results(self, run_id: str, kinetics: Dict) -> str:
        """
        Save kinetics calculation results
        
        Parameters:
        - run_id: Unique run identifier
        - kinetics: Dictionary with kinetics results
        
        Returns:
        - Path to saved file
        """
        # Create results dictionary
        results = {
            'run_id': run_id,
            'timestamp': datetime.now().isoformat(),
            'kinetics': kinetics
        }
        
        # Save as JSON
        filename = f"{run_id}_kinetics.json"
        filepath = os.path.join(self.processed_path, "kinetics_results", filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Also save as CSV for easy viewing
        csv_path = filepath.replace('.json', '.csv')
        self._kinetics_to_csv(kinetics, csv_path)
        
        return filepath
    
    def save_comparison(self, comparison_data: pd.DataFrame, name: str) -> str:
        """
        Save comparison results
        
        Parameters:
        - comparison_data: DataFrame with comparison results
        - name: Name for this comparison
        
        Returns:
        - Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.csv"
        filepath = os.path.join(self.comparisons_path, filename)
        
        comparison_data.to_csv(filepath, index=False)
        
        return filepath
    
    def get_all_runs(self) -> pd.DataFrame:
        """Get all runs with their metadata"""
        runs_db_path = os.path.join(self.metadata_path, "runs_database.csv")

        if os.path.exists(runs_db_path):
            return pd.read_csv(runs_db_path)
        else:
            return pd.DataFrame()

    def get_runs_summary(self) -> pd.DataFrame:
        """Return summary of all runs for dashboard, with parsed dates."""
        runs_df = self.get_all_runs()
        if not runs_df.empty and "upload_date" in runs_df.columns:
            runs_df["upload_date"] = pd.to_datetime(
                runs_df["upload_date"], errors="coerce")
            runs_df = runs_df.sort_values("upload_date", ascending=False)
        return runs_df

    def get_run_by_id(self, run_id: str) -> Optional[Dict]:
        """Get run data by ID"""
        # Get metadata
        metadata_path = os.path.join(self.metadata_path, f"{run_id}_metadata.json")
        if not os.path.exists(metadata_path):
            return None

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Get raw data
        raw_path = metadata.get('saved_path')
        if raw_path and os.path.exists(raw_path):
            metadata['data'] = pd.read_csv(raw_path)

        # Get kinetics if available
        kinetics_path = os.path.join(self.processed_path, "kinetics_results", f"{run_id}_kinetics.json")
        if os.path.exists(kinetics_path):
            with open(kinetics_path, 'r') as f:
                metadata['kinetics'] = json.load(f)

        return metadata

    def search_runs(self, criteria: Dict) -> pd.DataFrame:
        """Search runs by criteria.

        Supported keys: strain, medium, project, tags, date_range,
        objective, bioreactor_type, or any column in runs_database.
        """
        runs_df = self.get_runs_summary()

        if runs_df.empty:
            return runs_df

        for key, value in criteria.items():
            if not value:
                continue
            if key == 'date_range' and isinstance(value, list) and len(value) == 2:
                runs_df = runs_df[
                    (runs_df['upload_date'] >= value[0]) &
                    (runs_df['upload_date'] <= value[1])
                ]
            elif key in ('strain', 'medium', 'project', 'tags', 'objective'):
                if key in runs_df.columns:
                    runs_df = runs_df[
                        runs_df[key].str.contains(value, case=False, na=False)]
            elif key in runs_df.columns:
                runs_df = runs_df[runs_df[key] == value]

        return runs_df
    
    def delete_run(self, run_id: str) -> bool:
        """Delete a run and all associated files"""
        try:
            # Delete metadata
            metadata_path = os.path.join(self.metadata_path, f"{run_id}_metadata.json")
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            # Delete kinetics results
            kinetics_path = os.path.join(self.processed_path, "kinetics_results", f"{run_id}_kinetics.json")
            if os.path.exists(kinetics_path):
                os.remove(kinetics_path)
                csv_path = kinetics_path.replace('.json', '.csv')
                if os.path.exists(csv_path):
                    os.remove(csv_path)
            
            # Update runs database
            runs_df = self.get_all_runs()
            if not runs_df.empty:
                runs_df = runs_df[runs_df['run_id'] != run_id]
                runs_df.to_csv(os.path.join(self.metadata_path, "runs_database.csv"), index=False)
            
            return True
        except Exception as e:
            print(f"Error deleting run {run_id}: {e}")
            return False
    
    def export_run(self, run_id: str, format: str = 'excel') -> str:
        """
        Export run data in specified format
        
        Parameters:
        - run_id: Run identifier
        - format: 'excel', 'csv', or 'json'
        
        Returns:
        - Path to exported file
        """
        run_data = self.get_run_by_id(run_id)
        if not run_data:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{run_id}_export_{timestamp}"
        
        if format == 'excel':
            filepath = os.path.join(self.reports_path, f"{filename}.xlsx")
            with pd.ExcelWriter(filepath) as writer:
                # Raw data sheet
                if 'data' in run_data:
                    run_data['data'].to_excel(writer, sheet_name='Raw Data', index=False)
                
                # Kinetics sheet
                if 'kinetics' in run_data:
                    kinetics_df = pd.DataFrame([run_data['kinetics']['kinetics']])
                    kinetics_df.to_excel(writer, sheet_name='Kinetics', index=False)
                
                # Metadata sheet
                metadata_df = pd.DataFrame([{k:v for k,v in run_data.items() 
                                            if not isinstance(v, (pd.DataFrame, dict))}])
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        elif format == 'csv':
            filepath = os.path.join(self.reports_path, f"{filename}.csv")
            if 'data' in run_data:
                run_data['data'].to_csv(filepath, index=False)
        
        else:  # json
            filepath = os.path.join(self.reports_path, f"{filename}.json")
            with open(filepath, 'w') as f:
                json.dump(run_data, f, indent=2, default=str)
        
        return filepath
    
    def _generate_run_id(self, metadata: Dict) -> str:
        """Generate unique run ID"""
        # Create base string from metadata
        base_string = f"{metadata.get('strain', 'unknown')}_{metadata.get('medium', 'unknown')}_{datetime.now().isoformat()}"
        # Generate hash
        run_hash = hashlib.md5(base_string.encode()).hexdigest()[:8]
        # Format: YYYYMMDD_STRAIN_HASH
        run_id = f"{datetime.now().strftime('%Y%m%d')}_{metadata.get('strain', 'unknown')[:8]}_{run_hash}"
        return run_id
    
    def _update_runs_database(self, metadata: Dict):
        """Update the main runs database"""
        runs_db_path = os.path.join(self.metadata_path, "runs_database.csv")
        
        # Load existing database or create new
        if os.path.exists(runs_db_path):
            runs_df = pd.read_csv(runs_db_path)
        else:
            runs_df = pd.DataFrame()
        
        # Prepare new row
        new_row = {
            'run_id': metadata['run_id'],
            'original_filename': metadata['original_filename'],
            'upload_date': metadata['upload_date'],
            'strain': metadata.get('strain', ''),
            'medium': metadata.get('medium', ''),
            'objective': metadata.get('objective', ''),
            'project': metadata.get('project', ''),
            'tags': metadata.get('tags', ''),
            'bioreactor_type': metadata.get('bioreactor_type', ''),
            'volume_L': metadata.get('volume_L', ''),
            'temperature_C': metadata.get('temperature_C', ''),
            'pH': metadata.get('pH', ''),
            'notes': metadata.get('notes', '')
        }
        
        # Append
        runs_df = pd.concat([runs_df, pd.DataFrame([new_row])], ignore_index=True)
        runs_df.to_csv(runs_db_path, index=False)
    
    def _kinetics_to_csv(self, kinetics: Dict, filepath: str):
        """Convert kinetics dict to CSV for easy viewing"""
        # Flatten the kinetics dictionary
        flat_kinetics = {}
        
        def flatten_dict(d, parent_key=''):
            for k, v in d.items():
                new_key = f"{parent_key}_{k}" if parent_key else k
                if isinstance(v, dict):
                    flatten_dict(v, new_key)
                elif isinstance(v, list):
                    flat_kinetics[new_key] = str(v)
                else:
                    flat_kinetics[new_key] = v
        
        flatten_dict(kinetics)
        
        # Save to CSV
        pd.DataFrame([flat_kinetics]).to_csv(filepath, index=False)

# ============================================================================
# STREAMLIT UI COMPONENTS FOR DATA MANAGEMENT
# ============================================================================

def render_run_metadata_form():
    """Render form for entering run metadata"""
    
    st.subheader("📝 Run Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        strain = st.text_input("Strain", placeholder="e.g., E. coli MG1655")
        medium = st.text_input("Medium", placeholder="e.g., Glucose minimal")
        volume = st.number_input("Volume (L)", min_value=0.1, value=2.5)
    
    with col2:
        bioreactor = st.selectbox("Bioreactor Type", 
                                   ["Lab-scale batch", "Bench-top", "Pilot-scale", "Production"])
        temperature = st.number_input("Temperature (°C)", min_value=4.0, max_value=60.0, value=37.0)
        ph = st.number_input("pH", min_value=4.0, max_value=9.0, value=7.0, step=0.1)
    
    with col3:
        project = st.text_input("Project", placeholder="e.g., Media Optimization 2025")
        objective = st.text_input("Objective", placeholder="e.g., Compare carbon sources")
        tags = st.text_input("Tags", placeholder="comma-separated")
        notes = st.text_area("Notes", height=80)

    return {
        'strain': strain,
        'medium': medium,
        'volume_L': volume,
        'bioreactor_type': bioreactor,
        'temperature_C': temperature,
        'pH': ph,
        'project': project,
        'objective': objective,
        'tags': tags,
        'notes': notes
    }

def render_run_selector(data_manager: DataManager):
    """Render run selector for loading previous runs"""
    
    runs_df = data_manager.get_all_runs()
    
    if runs_df.empty:
        st.info("No runs found. Upload a file to get started.")
        return None
    
    st.subheader("📂 Load Previous Run")
    
    # Create selection options
    runs_df['display_name'] = runs_df.apply(
        lambda x: f"{x['run_id']} - {x['strain']} on {x['medium']} ({x['upload_date'][:10]})", 
        axis=1
    )
    
    selected_run = st.selectbox(
        "Select a run to load",
        runs_df['display_name'].tolist()
    )
    
    if selected_run:
        run_id = runs_df[runs_df['display_name'] == selected_run]['run_id'].iloc[0]
        run_data = data_manager.get_run_by_id(run_id)
        
        if run_data:
            st.success(f"Loaded: {run_data['original_filename']}")
            
            # Show run summary
            with st.expander("Run Summary"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Strain:** {run_data.get('strain', 'N/A')}")
                    st.write(f"**Medium:** {run_data.get('medium', 'N/A')}")
                    st.write(f"**Volume:** {run_data.get('volume_L', 'N/A')} L")
                with col2:
                    st.write(f"**Date:** {run_data.get('upload_date', 'N/A')[:10]}")
                    st.write(f"**Temperature:** {run_data.get('temperature_C', 'N/A')} °C")
                    st.write(f"**pH:** {run_data.get('pH', 'N/A')}")
            
            return run_data
    
    return None

def render_project_sidebar(data_manager: DataManager):
    """Render project management sidebar"""
    
    with st.sidebar:
        st.markdown("---")
        st.header("📁 Project Management")
        
        # Run statistics
        runs_df = data_manager.get_all_runs()
        if not runs_df.empty:
            st.metric("Total Runs", len(runs_df))
            
            # Recent runs
            with st.expander("Recent Runs"):
                recent = runs_df.sort_values('upload_date', ascending=False).head(5)
                for _, row in recent.iterrows():
                    st.write(f"• {row['run_id']}")
                    st.caption(f"  {row['strain']} | {row['medium']}")
        
        # Search
        st.subheader("🔍 Search Runs")
        search_strain = st.text_input("Strain")
        search_medium = st.text_input("Medium")
        
        if search_strain or search_medium:
            criteria = {}
            if search_strain:
                criteria['strain'] = search_strain
            if search_medium:
                criteria['medium'] = search_medium
            
            results = data_manager.search_runs(criteria)
            if not results.empty:
                st.write(f"Found {len(results)} runs:")
                for _, row in results.iterrows():
                    st.write(f"• {row['run_id']}")
            else:
                st.info("No matches found")