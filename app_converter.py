from flask import Flask, render_template, request
from pyliftover import LiftOver
import requests

app = Flask(__name__)

# Initialize LiftOver objects globally
lo_37_to_38 = LiftOver('hg19', 'hg38')
lo_38_to_37 = LiftOver('hg38', 'hg19')

def get_variant_details(chr_num, position):
    """
    Fetch gene names and RSIDs for a given chromosome and position.
    """
    server = "https://rest.ensembl.org"
    ext = f"/overlap/region/human/{chr_num}:{position}-{position}"
    headers = {"Content-Type": "application/json"}
    
    # Fetch gene names
    genes_response = requests.get(f"{server}{ext}?feature=gene", headers=headers)
    genes = genes_response.json() if genes_response.ok else []
    gene_names = ", ".join([g.get("external_name", "N/A") for g in genes]) if genes else "Not Available"
    
    # Fetch RSIDs
    variants_response = requests.get(f"{server}{ext}?feature=variation", headers=headers)
    variants = variants_response.json() if variants_response.ok else []
    rsids = ", ".join([v.get("id", "N/A") for v in variants]) if variants else "Not Available"
    
    return {"gene_names": gene_names, "rsids": rsids}

@app.route('/', methods=['GET', 'POST'])
def index():
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
                original_details = get_variant_details(chr_num, position)
                converted_details = get_variant_details(conv_chr, conv_pos)
                result = {
                    'original_chr': chr_num,
                    'original_pos': position,
                    'converted_chr': conv_chr,
                    'converted_pos': conv_pos,
                    'original_gene_names': original_details['gene_names'],
                    'original_rsids': original_details['rsids'],
                    'converted_gene_names': converted_details['gene_names'],
                    'converted_rsids': converted_details['rsids']
                }
                return render_template("converter.html", converter_result=result)
            else:
                return render_template("converter.html", converter_error="Could not convert these coordinates.")
        except Exception as e:
            return render_template("converter.html", error=str(e))
    return render_template("converter.html")

if __name__ == '__main__':
    app.run(debug=True)