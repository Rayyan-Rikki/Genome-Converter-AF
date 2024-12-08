from flask import Flask, render_template, request, send_file
from pyliftover import LiftOver
import pandas as pd
import requests
import io

app = Flask(__name__)

# Initialize LiftOver objects globally
lo_37_to_38 = LiftOver('hg19', 'hg38')
lo_38_to_37 = LiftOver('hg38', 'hg19')

def get_variant_details(chr_num, position):
    """
    Fetch gene names and RSIDs using Ensembl API.
    """
    try:
        server = "https://rest.ensembl.org"
        ext = f"/overlap/region/human/{chr_num}:{position}-{position}"
        headers = {"Content-Type": "application/json"}
        
        # Fetch gene names
        genes_response = requests.get(f"{server}{ext}?feature=gene", headers=headers)
        genes = genes_response.json() if genes_response.ok else []
        gene_names = ", ".join([g.get('external_name', 'N/A') for g in genes]) if genes else "Not Available"
        
        # Fetch variant IDs
        variants_response = requests.get(f"{server}{ext}?feature=variation", headers=headers)
        variants = variants_response.json() if variants_response.ok else []
        variant_ids = ", ".join([v.get('id', 'N/A') for v in variants]) if variants else "Not Available"
        
        return {'gene_names': gene_names, 'variants': variant_ids}
    except Exception as e:
        print(f"Error fetching variant details: {e}")
        return {'gene_names': "Error", 'variants': "Error"}

def fetch_gnomad_frequencies(gene_symbol, position, ref_allele, alt_allele):
    """
    Fetch gnomAD frequencies using GraphQL API.
    """
    query = """
    query ($geneSymbol: String!, $dataset: DatasetId!) {
      gene(gene_symbol: $geneSymbol, reference_genome: GRCh38) {
        variants(dataset: $dataset) {
          variant_id
          pos
          ref
          alt
          genome {
            af
          }
          exome {
            af
          }
        }
      }
    }
    """
    variables = {
        "geneSymbol": gene_symbol,
        "dataset": "gnomad_r3"
    }
    url = "https://gnomad.broadinstitute.org/api"
    response = requests.post(url, json={"query": query, "variables": variables})
    
    if response.status_code == 200:
        data = response.json()
        variants = data.get("data", {}).get("gene", {}).get("variants", [])
        for variant in variants:
            if (
                variant["pos"] == position
                and variant["ref"] == ref_allele
                and variant["alt"] == alt_allele
            ):
                return {
                    "variant_id": variant["variant_id"],
                    "genome_af": variant["genome"]["af"] if variant["genome"] else "N/A",
                    "exome_af": variant["exome"]["af"] if variant["exome"] else "N/A",
                }
    else:
        raise Exception(f"gnomAD query failed with status {response.status_code}: {response.text}")

    return None

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    result = None
    error = None

    if request.method == 'POST':
        try:
            chr_num = request.form['chromosome']
            position = int(request.form['position'])
            conversion_type = request.form['conversion_type']

            if conversion_type == '37_to_38':
                converted = lo_37_to_38.convert_coordinate(chr_num, position)
            else:
                converted = lo_38_to_37.convert_coordinate(chr_num, position)

            if converted and len(converted) > 0:
                conv_chr, conv_pos = converted[0][:2]
                details = get_variant_details(conv_chr, conv_pos)
                result = {
                    'original_chr': chr_num,
                    'original_pos': position,
                    'converted_chr': conv_chr,
                    'converted_pos': conv_pos,
                    **details
                }
            else:
                error = "Could not convert these coordinates."
        except Exception as e:
            error = str(e)

    return render_template("converter.html", result=result, error=error)

@app.route('/gnomad', methods=['GET', 'POST'])
def gnomad():
    freq_result = None
    freq_error = None

    if request.method == 'POST':
        try:
            gene_symbol = request.form['gene_symbol']
            position = int(request.form['position'])
            ref_allele = request.form['ref_allele']
            alt_allele = request.form['alt_allele']

            freq_result = fetch_gnomad_frequencies(gene_symbol, position, ref_allele, alt_allele)

            if freq_result:
                freq_result["gene_symbol"] = gene_symbol  # Include gene symbol directly from input
            else:
                freq_error = "Variant not found in gnomAD data."
        except Exception as e:
            freq_error = str(e)

    return render_template("frequency.html", freq_result=freq_result, freq_error=freq_error)

if __name__ == '__main__':
    app.run(debug=True)