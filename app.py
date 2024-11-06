from flask import Flask, render_template, request, jsonify, send_file
from pyliftover import LiftOver
import pandas as pd
import requests
import io

app = Flask(__name__)

# Initialize LiftOver objects globally
lo_37_to_38 = LiftOver('hg19', 'hg38')
lo_38_to_37 = LiftOver('hg38', 'hg19')

def get_variant_details(chr_num, position):
    try:
        # Ensembl REST API endpoint
        server = "https://rest.ensembl.org"
        ext = f"/overlap/region/human/{chr_num}:{position}-{position}"
        headers = {"Content-Type": "application/json"}
        
        # Get genes
        genes_response = requests.get(f"{server}{ext}?feature=gene", headers=headers)
        genes = genes_response.json() if genes_response.ok else []
        gene_names = ", ".join([g.get('external_name', 'N/A') for g in genes]) if genes else "Not Available"
        
        # Get variants
        variants_response = requests.get(f"{server}{ext}?feature=variation", headers=headers)
        variants = variants_response.json() if variants_response.ok else []
        variant_ids = ", ".join([v.get('id', 'N/A') for v in variants]) if variants else "Not Available"
        
        # Get gnomAD frequencies (you'll need to implement this based on your data source)
        # This is a placeholder - you'll need to implement actual gnomAD API calls
        gnomad_freq = "Not Available"
        
        return {
            'gene_names': gene_names,
            'variants': variant_ids,
            'gnomad_freq': gnomad_freq
        }
    except Exception as e:
        print(f"Error fetching variant details: {str(e)}")
        return {
            'gene_names': "Error",
            'variants': "Error",
            'gnomad_freq': "Error"
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Check if it's a batch upload
            if 'file' in request.files:
                file = request.files['file']
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.filename.endswith('.txt'):
                    df = pd.read_csv(file, sep='\t')
                else:
                    return render_template('index.html', error="Please upload a CSV or TSV file")
                
                # Process batch conversion
                results = []
                for _, row in df.iterrows():
                    chr_num = str(row['chromosome'])
                    position = int(row['position'])
                    conversion_type = request.form['conversion_type']
                    
                    if conversion_type == '37_to_38':
                        converted = lo_37_to_38.convert_coordinate(chr_num, position)
                    else:
                        converted = lo_38_to_37.convert_coordinate(chr_num, position)
                    
                    if converted and len(converted) > 0:
                        conv_chr, conv_pos = converted[0][:2]
                        details = get_variant_details(conv_chr, conv_pos)
                        results.append({
                            'original_chr': chr_num,
                            'original_pos': position,
                            'converted_chr': conv_chr,
                            'converted_pos': conv_pos,
                            **details
                        })
                
                # Create output file
                output = pd.DataFrame(results)
                output_buffer = io.StringIO()
                output.to_csv(output_buffer, index=False)
                output_buffer.seek(0)
                
                return send_file(
                    io.BytesIO(output_buffer.getvalue().encode()),
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name='converted_coordinates.csv'
                )
            
            else:
                # Single conversion
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
                    return render_template('index.html', result=result)
                else:
                    return render_template('index.html', error="Could not convert these coordinates")
                
        except Exception as e:
            return render_template('index.html', error=str(e))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)