import pyopenms as oms
import pandas as pd
import requests
from pyopenms.plotting import plot_spectrum


def fetch_fasta_up(pid: str):

    resp = requests.get(f"https://rest.uniprot.org/uniprotkb/{pid}.fasta")

    if resp.ok:
        return resp.text


def parse_fasta_quick(fasta: str):

    lines = fasta.split("\n")

    desc = lines[0]
    seq_lines = lines[1:]

    seq = "".join(seq_lines)

    return({"desc": desc, "seq": seq})


def get_up_seq_quick(pid: str):

    fasta = fetch_fasta_up(pid)

    fasta_parsed = parse_fasta_quick(fasta)

    seq = fasta_parsed["seq"]

    return seq



def tryptic_digest(seq, misses = 2, min = 7, max = 30):
    
    peptides=[]
    cut_sites=[0]

    
    def append_if(seq):

        N = len(seq)
        
        if(N >= min and N <= max):
            peptides.append(seq)
    
    for i in range(0,len(seq)-1):
        if seq[i]=='K' and seq[i+1]!='P':
            cut_sites.append(i+1)
        elif seq[i]=='R' and seq[i+1]!='P':
            cut_sites.append(i+1)
    
    if cut_sites[-1]!=len(seq):
        cut_sites.append(len(seq))

    if len(cut_sites)>2:
        if  misses==0:
            for j in range(0,len(cut_sites)-1):
                append_if(seq[cut_sites[j]:cut_sites[j+1]])

        elif misses==1:
            for j in range(0,len(cut_sites)-2):
                append_if(seq[cut_sites[j]:cut_sites[j+1]])
                append_if(seq[cut_sites[j]:cut_sites[j+2]])
            
            append_if(seq[cut_sites[-2]:cut_sites[-1]])

        elif misses==2:
            for j in range(0,len(cut_sites)-3):
                append_if(seq[cut_sites[j]:cut_sites[j+1]])
                append_if(seq[cut_sites[j]:cut_sites[j+2]])
                append_if(seq[cut_sites[j]:cut_sites[j+3]])
            
            append_if(seq[cut_sites[-3]:cut_sites[-2]])
            append_if(seq[cut_sites[-3]:cut_sites[-1]])
            append_if(seq[cut_sites[-2]:cut_sites[-1]])
    else: #there is no trypsin site in the protein sequence
        return 0
    return peptides

def generate_theor_spectrum(sequence, add_losses = True, add_b = True, include_precursor = True, min_charge = 1, max_charge=3):

    tsg = oms.TheoreticalSpectrumGenerator()
    spectrum = oms.MSSpectrum()
    peptide = oms.AASequence.fromString(sequence)

    p = oms.Param()
    if add_b:
        p.setValue("add_b_ions", "true")

    if include_precursor:
        p.setValue("add_precursor_peaks", "true")
        p.setValue("add_all_precursor_charges", "true")

    p.setValue("add_metainfo", "true")

    if add_losses:
        p.setValue("add_losses", "true")

    tsg.setParameters(p)
    tsg.getSpectrum(spectrum, peptide, min_charge, max_charge)

    return(spectrum)


def print_theor_spectrum(spectrum):
    print("Spectrum 1 of", peptide, "has", spec1.size(), "peaks.")
    for ion, peak in zip(spectrum.getStringDataArrays()[0], spectrum):
        print(ion.decode(), "is generated at m/z", peak.getMZ())


def theor_spectrum_to_table(spectrum):
    df = pd.DataFrame([{"ion": ion, "mz": peak.getMZ()} for ion, peak in zip(spec.getStringDataArrays()[0], spectrum)])
    return df

def get_tryptic_mz(seq, misses = 2, min = 7, max = 30, max_charge = 3):

    tryptic_peptides = tryptic_digest(seq = trypsin_seq, misses = misses, min = min, max = max)

    entry_list = []


    for peptide in tryptic_peptides:

        pep_obj = oms.AASequence.fromString(peptide)

        for charge in range(1, max_charge+1):

            entry = {
            "id": f"{peptide}+{charge}",
            "mz": pep_obj.getMZ(charge)
            }

            entry_list.append(entry)

    entry_list.sort(key=lambda x: x["mz"])

    return pd.DataFrame(entry_list)
