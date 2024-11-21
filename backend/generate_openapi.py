import os

# Load environment variables
hostname = os.getenv("HOSTNAME", "klopta.vinnievirtuoso.online")

# Path to your template and the output file
template_path = "openapi_template.yaml"
output_path = "static/swagger-ui/openapi.yaml"

# Read the template
with open(template_path, "r") as file:
    content = file.read()

# Replace placeholders
content = content.replace("${HOSTNAME}", hostname)

# Write the updated content to the output file
with open(output_path, "w") as file:
    file.write(content)

print(f"Generated {output_path} with HOSTNAME={hostname}")
