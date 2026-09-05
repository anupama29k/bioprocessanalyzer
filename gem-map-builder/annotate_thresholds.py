"""
annotate_thresholds.py -- Add source_type, citation, confidence to threshold_audit.csv
"""
import csv

with open("threshold_audit.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames

# Citation DB: (organism, parameter) -> (source_type, citation, confidence)
C = {
    ("CHO","glucose"):("literature","Altamirano et al. 2006 J Biotechnol; Glacken et al. 1988 Biotechnol Bioeng","HIGH"),
    ("CHO","lactate"):("literature","Zagari et al. 2013 New Biotechnol; Luo et al. 2012 Biotechnol Bioeng","HIGH"),
    ("CHO","pH"):("literature","Li et al. 2010 Biotechnol Bioeng; Trummer et al. 2006 Biotechnol Bioeng","HIGH"),
    ("CHO","DO"):("literature","Restelli et al. 2006 Biotechnol Bioeng","HIGH"),
    ("CHO","ammonia"):("literature","Yang & Butler 2000 Biotechnol Bioeng; Chen & Bhargava 2011 Biotechnol Adv","HIGH"),
    ("CHO","VCD"):("literature","Huang et al. 2010 Biotechnol Bioeng","HIGH"),
    ("CHO","viability"):("regulatory","ICH Q5D; industry standard fed-batch harvest criteria","HIGH"),
    ("CHO","titer"):("domain_knowledge","Process-specific; typical CHO mAb range 1-10 g/L","MEDIUM"),
    ("CHO","CO2"):("literature","Gray et al. 1996 Cytotechnology; Goudar et al. 2006 Biotechnol Prog","MEDIUM"),
    ("CHO","O2"):("literature","Restelli et al. 2006 Biotechnol Bioeng (off-gas analysis)","MEDIUM"),
    ("CHO","temperature"):("literature","Kaufmann et al. 1999 Biotechnol Bioeng; Yoon et al. 2003 Biotechnol Bioeng","HIGH"),
    ("CHO","agitation"):("literature","Nienow et al. 2013 Biochem Eng J","MEDIUM"),
    ("CHO-S","glucose"):("literature","Clincke et al. 2013 Biotechnol Prog; Bielser et al. 2018 Biotechnol Adv","HIGH"),
    ("CHO-S","lactate"):("literature","Clincke et al. 2013 Biotechnol Prog","HIGH"),
    ("CHO-S","pH"):("literature","Pohlscheidt et al. 2013 Biotechnol Prog","HIGH"),
    ("CHO-S","DO"):("literature","Clincke et al. 2013 Biotechnol Prog","HIGH"),
    ("CHO-S","ammonia"):("literature","Bielser et al. 2018 Biotechnol Adv","MEDIUM"),
    ("CHO-S","VCD"):("literature","Clincke et al. 2013 Biotechnol Prog (60-120e6/mL perfusion)","HIGH"),
    ("CHO-S","viability"):("literature","Pohlscheidt et al. 2013 Biotechnol Prog","MEDIUM"),
    ("CHO-S","titer"):("domain_knowledge","Perfusion permeate titre typically 0.3-2.5 g/L","MEDIUM"),
    ("CHO-S","CO2"):("domain_knowledge","High-density perfusion CER; limited published data","NEEDS_VERIFICATION"),
    ("CHO-S","O2"):("domain_knowledge","High-density OUR from perfusion literature","NEEDS_VERIFICATION"),
    ("CHO-S","temperature"):("literature","Perfusion temp shift common; Clincke et al. 2013","MEDIUM"),
    ("CHO-S","agitation"):("literature","ATF/TFF shear considerations; Clincke et al. 2013","MEDIUM"),
    ("HEK293","glucose"):("literature","Grieger et al. 2016 Nat Protoc; Henry et al. 2011 Biotechnol Bioeng","MEDIUM"),
    ("HEK293","lactate"):("literature","Cervera et al. 2013 J Biotechnol; Blessing et al. 2019 Mol Ther","MEDIUM"),
    ("HEK293","pH"):("literature","Grieger et al. 2016 Nat Protoc","HIGH"),
    ("HEK293","DO"):("literature","Emmerling et al. 2016 Hum Gene Ther Methods","MEDIUM"),
    ("HEK293","ammonia"):("domain_knowledge","Extrapolated from mammalian; HEK293-specific data sparse","NEEDS_VERIFICATION"),
    ("HEK293","VCD"):("literature","Grieger et al. 2016 Nat Protoc (transfection density 1.5-2.5e6)","HIGH"),
    ("HEK293","viability"):("literature","Naso et al. 2017 BioDrugs; post-transfection drop expected","HIGH"),
    ("HEK293","titer"):("literature","Grieger et al. 2016 Nat Protoc (AAV vg/mL); Blessing et al. 2019","HIGH"),
    ("HEK293","CO2"):("domain_knowledge","Extrapolated from mammalian; HEK293-specific CER not published","NEEDS_VERIFICATION"),
    ("HEK293","O2"):("domain_knowledge","Extrapolated from mammalian off-gas; limited HEK293 data","NEEDS_VERIFICATION"),
    ("HEK293","temperature"):("literature","Grieger et al. 2016 Nat Protoc","HIGH"),
    ("HEK293","agitation"):("literature","Grieger et al. 2016 Nat Protoc; HEK293 shear sensitivity","MEDIUM"),
    ("NS0","glucose"):("literature","Mostafa & Gu 2003 Biotechnol Prog","MEDIUM"),
    ("NS0","lactate"):("literature","Seth et al. 2006 Biotechnol Bioeng; Mostafa & Gu 2003","MEDIUM"),
    ("NS0","pH"):("literature","Omasa et al. 2010 J Biosci Bioeng","MEDIUM"),
    ("NS0","DO"):("literature","Mostafa & Gu 2003 Biotechnol Prog","MEDIUM"),
    ("NS0","ammonia"):("literature","Schneider et al. 1996 J Biotechnol; Yang & Butler 2000 (GS-deficient)","HIGH"),
    ("NS0","VCD"):("literature","Mostafa & Gu 2003 Biotechnol Prog","MEDIUM"),
    ("NS0","viability"):("domain_knowledge","NS0 cholesterol auxotrophy limits recovery; threshold extrapolated","NEEDS_VERIFICATION"),
    ("NS0","titer"):("domain_knowledge","NS0 typically lower yielding than CHO; process-specific","MEDIUM"),
    ("NS0","CO2"):("domain_knowledge","Extrapolated from mammalian; NS0-specific CER not published","NEEDS_VERIFICATION"),
    ("NS0","O2"):("domain_knowledge","Extrapolated from mammalian off-gas","NEEDS_VERIFICATION"),
    ("NS0","temperature"):("domain_knowledge","Standard mammalian 37C; NS0-specific temp shift data limited","NEEDS_VERIFICATION"),
    ("NS0","agitation"):("domain_knowledge","NS0 moderate shear sensitivity; limited published data","NEEDS_VERIFICATION"),
    ("Sp2/0","glucose"):("literature","Europa et al. 2000 Biotechnol Bioeng","MEDIUM"),
    ("Sp2/0","lactate"):("literature","Europa et al. 2000 Biotechnol Bioeng; Ljunggren & Haggstrom 1994","MEDIUM"),
    ("Sp2/0","pH"):("literature","Ljunggren & Haggstrom 1994 Biotechnol Bioeng","MEDIUM"),
    ("Sp2/0","DO"):("domain_knowledge","Hybridoma DO extrapolated; Sp2/0-specific limited","NEEDS_VERIFICATION"),
    ("Sp2/0","ammonia"):("literature","Ljunggren & Haggstrom 1994 Biotechnol Bioeng","MEDIUM"),
    ("Sp2/0","VCD"):("literature","Ljunggren & Haggstrom 1994 Biotechnol Bioeng","MEDIUM"),
    ("Sp2/0","viability"):("domain_knowledge","Hybridoma fragility; specific threshold data sparse","NEEDS_VERIFICATION"),
    ("Sp2/0","titer"):("domain_knowledge","Hybridoma mAb typically 0.1-2 g/L; process-specific","MEDIUM"),
    ("Sp2/0","CO2"):("domain_knowledge","Extrapolated from mammalian","NEEDS_VERIFICATION"),
    ("Sp2/0","O2"):("domain_knowledge","Extrapolated from mammalian off-gas","NEEDS_VERIFICATION"),
    ("Sp2/0","temperature"):("domain_knowledge","Standard mammalian 37C; hybridoma temp sensitivity","NEEDS_VERIFICATION"),
    ("Sp2/0","agitation"):("literature","Michaels et al. 1991 Biotechnol Bioeng (hybridoma shear)","MEDIUM"),
    ("BHK-21","glucose"):("literature","Merten et al. 1994 Cytotechnology","MEDIUM"),
    ("BHK-21","lactate"):("literature","Merten et al. 1994 Cytotechnology","MEDIUM"),
    ("BHK-21","pH"):("literature","Merten et al. 1994 Cytotechnology","MEDIUM"),
    ("BHK-21","DO"):("domain_knowledge","Extrapolated from mammalian; BHK-specific DO limited","NEEDS_VERIFICATION"),
    ("BHK-21","ammonia"):("domain_knowledge","BHK ammonia thresholds poorly characterized","NEEDS_VERIFICATION"),
    ("BHK-21","VCD"):("literature","Merten et al. 1994 Cytotechnology; Telling & Elsworth 1965","MEDIUM"),
    ("BHK-21","viability"):("literature","Merten et al. 1994 Cytotechnology (CPE context)","MEDIUM"),
    ("BHK-21","titer"):("domain_knowledge","Vaccine/coag factor titre; product-specific units","NEEDS_VERIFICATION"),
    ("BHK-21","CO2"):("domain_knowledge","Extrapolated from mammalian","NEEDS_VERIFICATION"),
    ("BHK-21","O2"):("domain_knowledge","Extrapolated from mammalian off-gas","NEEDS_VERIFICATION"),
    ("BHK-21","temperature"):("literature","Telling & Elsworth 1965 Biotechnol Bioeng","MEDIUM"),
    ("BHK-21","agitation"):("literature","Croughan et al. 1987 Biotechnol Bioeng (microcarrier shear)","MEDIUM"),
    ("E. coli","glucose"):("literature","Lee 1996 Trends Biotechnol; Eiteman & Altman 2006 Trends Biotechnol","HIGH"),
    ("E. coli","acetate"):("literature","Luli & Strohl 1990 Appl Environ Microbiol; Eiteman & Altman 2006","HIGH"),
    ("E. coli","pH"):("literature","Shiloach & Fass 2005 Biotechnol Adv","HIGH"),
    ("E. coli","DO"):("literature","Shiloach & Fass 2005 Biotechnol Adv; Lara et al. 2006 Mol Biotechnol","HIGH"),
    ("E. coli","ammonia"):("literature","Riesenberg et al. 1991 J Biotechnol; Shiloach & Fass 2005","HIGH"),
    ("E. coli","OD600"):("literature","Korz et al. 1995 J Biotechnol; Riesenberg & Guthke 1999","HIGH"),
    ("E. coli","viability"):("domain_knowledge","E. coli viability method-dependent (plate counts vs flow)","NEEDS_VERIFICATION"),
    ("E. coli","titer"):("literature","Yee & Blanch 1992 Biotechnol Bioeng; strain/expression dependent","MEDIUM"),
    ("E. coli","CO2"):("domain_knowledge","CER monitoring in HCDC; limited standardized thresholds","NEEDS_VERIFICATION"),
    ("E. coli","O2"):("literature","Shiloach & Fass 2005 (OUR/CER monitoring)","MEDIUM"),
    ("E. coli","temperature"):("textbook","Baneyx 1999 Curr Opin Biotechnol; Neidhardt et al. Physiology of the Bacterial Cell","HIGH"),
    ("E. coli","agitation"):("literature","Shiloach & Fass 2005; Garcia-Ochoa & Gomez 2009 Biotechnol Adv","MEDIUM"),
    ("B. subtilis","glucose"):("literature","Dauner et al. 2001 Biotechnol Bioeng; Spo0A sporulation literature","MEDIUM"),
    ("B. subtilis","acetoin"):("literature","Renna et al. 1993 J Bacteriol (alsSD operon)","MEDIUM"),
    ("B. subtilis","pH"):("literature","Hahne et al. 2010 J Proteome Res; subtilisin alkaline protease context","MEDIUM"),
    ("B. subtilis","DO"):("literature","Cruz Ramos et al. 2000 J Bacteriol (anaerobic regulon)","MEDIUM"),
    ("B. subtilis","ammonia"):("literature","Fisher 1999 Mol Microbiol (GlnR regulon)","MEDIUM"),
    ("B. subtilis","OD600"):("domain_knowledge","Growth curves; sporulation transition density process-specific","NEEDS_VERIFICATION"),
    ("B. subtilis","viability"):("domain_knowledge","Autolysis (LytC/LytD) complicates measurement; Smith et al. 2000","NEEDS_VERIFICATION"),
    ("B. subtilis","titer"):("literature","Westers et al. 2004 BBA; native enzyme 20-25 g/L","MEDIUM"),
    ("B. subtilis","CO2"):("domain_knowledge","CER in B. subtilis fermentation; limited standardized data","NEEDS_VERIFICATION"),
    ("B. subtilis","O2"):("literature","Obligate aerobe; OUR from Dauner et al. 2001","MEDIUM"),
    ("B. subtilis","temperature"):("textbook","Hecker et al. 2007 Microbiology (sigB stress)","HIGH"),
    ("B. subtilis","agitation"):("literature","Surfactin foaming from Cooper et al. 1981; kLa for aerobe","MEDIUM"),
    ("P. pastoris","glucose"):("literature","Cos et al. 2006 Biotechnol Bioeng; Cereghino & Cregg 2000 FEMS","HIGH"),
    ("P. pastoris","methanol"):("literature","Cos et al. 2006 Biotechnol Bioeng; Looser et al. 2015 Biotechnol Adv","HIGH"),
    ("P. pastoris","ethanol"):("literature","Cos et al. 2006 (Crabtree-negative overflow)","MEDIUM"),
    ("P. pastoris","pH"):("literature","Cos et al. 2006 Biotechnol Bioeng; Potvin et al. 2012 Biotechnol Adv","HIGH"),
    ("P. pastoris","DO"):("literature","Cos et al. 2006 Biotechnol Bioeng (AOX O2 demand)","HIGH"),
    ("P. pastoris","ammonia"):("domain_knowledge","Pichia nitrogen; limited organism-specific threshold studies","NEEDS_VERIFICATION"),
    ("P. pastoris","OD600"):("literature","Cos et al. 2006; Potvin et al. 2012 (OD 200-500)","HIGH"),
    ("P. pastoris","viability"):("domain_knowledge","Methanol toxicity viability; limited published thresholds","NEEDS_VERIFICATION"),
    ("P. pastoris","titer"):("literature","Cos et al. 2006; Looser et al. 2015 (secreted protein range)","MEDIUM"),
    ("P. pastoris","CO2"):("literature","Cos et al. 2006 (CER/RQ for methanol phase)","MEDIUM"),
    ("P. pastoris","O2"):("literature","Cos et al. 2006 (highest OUR of any bioprocess)","HIGH"),
    ("P. pastoris","temperature"):("literature","Cos et al. 2006; Looser et al. 2015","HIGH"),
    ("P. pastoris","agitation"):("literature","Cos et al. 2006; Potvin et al. 2012 (high-density kLa)","MEDIUM"),
    ("S. cerevisiae","glucose"):("literature","Verduyn et al. 1992 Yeast; De Deken 1966 J Gen Microbiol","HIGH"),
    ("S. cerevisiae","ethanol"):("literature","Verduyn et al. 1992 Yeast; Ingledew 1999 ethanol tolerance","HIGH"),
    ("S. cerevisiae","pH"):("literature","Verduyn et al. 1992 Yeast; Castan et al. 2002 Biotechnol Bioeng","HIGH"),
    ("S. cerevisiae","DO"):("literature","Verduyn et al. 1992; van Dijken et al. 2000 Enzyme Microb Technol","HIGH"),
    ("S. cerevisiae","ammonia"):("literature","ter Schure et al. 2000 FEMS Microbiol Rev (NCR)","HIGH"),
    ("S. cerevisiae","OD600"):("literature","Castan et al. 2002 Biotechnol Bioeng","MEDIUM"),
    ("S. cerevisiae","viability"):("domain_knowledge","Yeast autolysis; viability thresholds process-specific","NEEDS_VERIFICATION"),
    ("S. cerevisiae","titer"):("domain_knowledge","VLP/antigen; product and promoter dependent","NEEDS_VERIFICATION"),
    ("S. cerevisiae","CO2"):("literature","Verduyn et al. 1992 (RQ/CER for Crabtree)","MEDIUM"),
    ("S. cerevisiae","O2"):("literature","van Dijken et al. 2000 Enzyme Microb Technol","MEDIUM"),
    ("S. cerevisiae","temperature"):("textbook","Morano et al. 2012 Genetics; Verduyn et al. 1992","HIGH"),
    ("S. cerevisiae","agitation"):("domain_knowledge","Yeast shear tolerant; foam is primary concern","MEDIUM"),
}

# Strain-specific overrides: (organism, strain, param) -> (src, cite, conf)
S = {
    ("CHO","CHO-DG44","glucose"):("literature","Urlaub & Chasin 1980 PNAS; Kaufman 1990 Methods Enzymol","MEDIUM"),
    ("CHO","CHO-DG44","lactate"):("domain_knowledge","DG44 higher glycolytic flux; 20-30% more lactate than K1","NEEDS_VERIFICATION"),
    ("CHO","CHO-DG44","VCD"):("domain_knowledge","DG44 lower peak due to MTX amplification burden","NEEDS_VERIFICATION"),
    ("CHO","CHO-DG44","titer"):("literature","Kaufman 1990 Methods Enzymol (DHFR-MTX amplification)","MEDIUM"),
    ("CHO","CHO-DG44","ammonia"):("domain_knowledge","DG44 ammonia sensitivity; limited comparative data","NEEDS_VERIFICATION"),
    ("CHO","CHO-GS","ammonia"):("literature","Bebbington et al. 1992 Bio/Technology; Barnes et al. 2001 Cytotechnology","HIGH"),
    ("CHO","CHO-GS","lactate"):("domain_knowledge","GS system cleaner metabolism; less lactate than DHFR","MEDIUM"),
    ("CHO","CHO-GS","titer"):("literature","Fan et al. 2012 Biotechnol Bioeng (GS-CHO system)","MEDIUM"),
    ("CHO","CHO-GS","VCD"):("domain_knowledge","GS-CHO growth under MSX selection","MEDIUM"),
    ("HEK293","HEK293T","titer"):("literature","Dull et al. 1998 J Virol; Naldini et al. 1996 Science","HIGH"),
    ("HEK293","HEK293T","VCD"):("literature","Grieger et al. 2016 Nat Protoc (293T density)","MEDIUM"),
    ("HEK293","HEK293T","viability"):("literature","293T SV40 T fragility; Bhatt et al. 2021 Mol Ther Methods","MEDIUM"),
    ("HEK293","HEK293F","VCD"):("literature","Backliwal et al. 2008 Biotechnol Bioeng (FreeStyle 293-F)","MEDIUM"),
    ("HEK293","HEK293F","agitation"):("literature","FreeStyle system 125 rpm orbital shaker protocol","MEDIUM"),
    ("HEK293","HEK293F","lactate"):("domain_knowledge","293F serum-free; limited metabolic comparisons","NEEDS_VERIFICATION"),
    ("P. pastoris","X-33","methanol"):("literature","Cos et al. 2006 (Mut+ AOX1+AOX2)","HIGH"),
    ("P. pastoris","X-33","DO"):("literature","Cos et al. 2006 (Mut+ highest OUR)","HIGH"),
    ("P. pastoris","KM71H","methanol"):("literature","Cos et al. 2006 (MutS AOX1 disrupted)","HIGH"),
    ("P. pastoris","KM71H","DO"):("literature","Cos et al. 2006 (MutS lower OUR)","HIGH"),
    ("P. pastoris","KM71H","titer"):("domain_knowledge","MutS trades speed for controllability","MEDIUM"),
    ("P. pastoris","KM71H","agitation"):("domain_knowledge","KM71H lower O2 demand","NEEDS_VERIFICATION"),
    ("S. cerevisiae","BY4741","OD600"):("literature","Brachmann et al. 1998 Yeast (S288C auxotrophy)","MEDIUM"),
    ("S. cerevisiae","BY4741","titer"):("domain_knowledge","Lab strain not optimized","NEEDS_VERIFICATION"),
    ("S. cerevisiae","BY4741","glucose"):("literature","Otterstedt et al. 2004 EMBO Rep (S288C Crabtree)","MEDIUM"),
    ("S. cerevisiae","CEN.PK","OD600"):("literature","van Dijken et al. 2000 Enzyme Microb Technol","HIGH"),
    ("S. cerevisiae","CEN.PK","ethanol"):("literature","van Dijken et al. 2000 (lower Crabtree than S288C)","MEDIUM"),
    ("S. cerevisiae","CEN.PK","titer"):("domain_knowledge","Industrial reference; metabolic engineering preferred","MEDIUM"),
    ("S. cerevisiae","CEN.PK","glucose"):("literature","van Dijken et al. 2000","MEDIUM"),
    ("S. cerevisiae","W303","OD600"):("literature","Ralser et al. 2012 PLoS One","MEDIUM"),
    ("S. cerevisiae","W303","viability"):("domain_knowledge","W303 less robust than CEN.PK","NEEDS_VERIFICATION"),
    ("S. cerevisiae","W303","titer"):("domain_knowledge","Research strain; ade2 may affect folding","NEEDS_VERIFICATION"),
    ("E. coli","BL21(DE3)","titer"):("literature","Studier & Moffatt 1986 J Mol Biol (T7 system)","HIGH"),
    ("E. coli","BL21(DE3)","viability"):("literature","Studier et al. 2009 Protein Expr Purif (lon/ompT)","MEDIUM"),
    ("E. coli","BL21(DE3)","temperature"):("literature","Baneyx 1999 Curr Opin Biotechnol","HIGH"),
    ("E. coli","BL21 Star","titer"):("literature","Lopez et al. 2009 Microb Cell Fact (rne131)","MEDIUM"),
    ("E. coli","BL21 Star","viability"):("domain_knowledge","Higher expression burden; faster viability decline","NEEDS_VERIFICATION"),
    ("E. coli","HMS174(DE3)","OD600"):("domain_knowledge","K-12 derivative lower density; recA- stability","NEEDS_VERIFICATION"),
    ("E. coli","HMS174(DE3)","titer"):("domain_knowledge","Active restriction; lower expression than BL21","NEEDS_VERIFICATION"),
    ("E. coli","HMS174(DE3)","acetate"):("domain_knowledge","K-12 vs B-strain acetate metabolism","NEEDS_VERIFICATION"),
    ("E. coli","K-12 MG1655","OD600"):("literature","Blattner et al. 1997 Science (MG1655 genome)","HIGH"),
    ("E. coli","K-12 MG1655","titer"):("domain_knowledge","Active lon/ompT degrade recombinant protein","MEDIUM"),
    ("E. coli","K-12 MG1655","acetate"):("literature","Kumari et al. 2000 J Bacteriol (acs in K-12)","MEDIUM"),
    ("E. coli","W3110","OD600"):("literature","Yoon et al. 2009 Biotechnol Bioeng","MEDIUM"),
    ("E. coli","W3110","titer"):("regulatory","FDA-approved lineage for Humulin; Eli Lilly process","HIGH"),
    ("E. coli","W3110","acetate"):("literature","Well-characterized overflow; extensive fed-batch protocols","MEDIUM"),
    ("E. coli","W3110","temperature"):("literature","Swartz 2001 Curr Opin Biotechnol (28-30C soluble)","MEDIUM"),
}

for row in rows:
    org, strain, param = row["organism"], row["strain"], row["parameter"]
    key3 = (org, strain, param)
    key2 = (org, param)
    if key3 in S:
        src, cite, conf = S[key3]
    elif key2 in C:
        src, cite, conf = C[key2]
    else:
        src, cite, conf = "AI_generated", "No published reference identified; threshold estimated", "NEEDS_VERIFICATION"
    row["source_type"] = src
    row["citation"] = cite
    row["confidence"] = conf

out_fields = fieldnames + ["source_type", "citation", "confidence"]
with open("threshold_audit.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=out_fields)
    writer.writeheader()
    writer.writerows(rows)

# Summary
cc = {}
sc = {}
for r in rows:
    cc[r["confidence"]] = cc.get(r["confidence"], 0) + 1
    sc[r["source_type"]] = sc.get(r["source_type"], 0) + 1

print(f"Written {len(rows)} annotated rows to threshold_audit.csv")
print(f"\nConfidence:  HIGH={cc.get('HIGH',0)}  MEDIUM={cc.get('MEDIUM',0)}  NEEDS_VERIFICATION={cc.get('NEEDS_VERIFICATION',0)}")
print(f"Sources:     literature={sc.get('literature',0)}  domain_knowledge={sc.get('domain_knowledge',0)}  "
      f"textbook={sc.get('textbook',0)}  regulatory={sc.get('regulatory',0)}  AI_generated={sc.get('AI_generated',0)}")

nv = [r for r in rows if r["confidence"] == "NEEDS_VERIFICATION"]
print(f"\nNEEDS_VERIFICATION: {len(nv)} rows flagged")
for r in nv:
    print(f"  {r['organism']:<16} {r['strain']:<14} {r['parameter']:<12} {r['citation'][:55]}")
