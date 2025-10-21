$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory=$true)][string]$Question,
    [string]$OutDir = "./streamlit_output",
    [string]$Model = "me-mii-consultant"
)

Write-Host "Creating/Updating Ollama model '$Model' from Modelfile..."
ollama create $Model -f Modelfile | Out-Null

Write-Host "Querying consultant..."
python rag_consultant.py "$Question" --out $OutDir --model $Model



