from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def fetch_gnomad_frequencies(gene_symbol, position, ref_allele, alt_allele):
    """
    Fetch allele frequencies from gnomAD for a specific variant.
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            gene_symbol = request.form['gene_symbol']
            position = int(request.form['position'])
            ref_allele = request.form['ref_allele']
            alt_allele = request.form['alt_allele']

            result = fetch_gnomad_frequencies(gene_symbol, position, ref_allele, alt_allele)

            if result:
                return render_template("frequency.html", freq_result=result)
            else:
                return render_template("frequency.html", freq_error="Variant not found in gnomAD data.")
        except Exception as e:
            return render_template("frequency.html", error=str(e))
    return render_template("frequency.html")

if __name__ == '__main__':
    app.run(debug=True)