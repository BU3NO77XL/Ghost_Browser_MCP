Restore
use o ghost browser mcp para clonar este site pixel perfect https://www.gov.br/pt-br



Kiro
Vou usar o Ghost Browser MCP para clonar o site pixel perfect. Deixa eu começar capturando toda a estrutura e assets.


Called MCP tool

ghost_browser_mcp / spawn_browser

Called MCP tool

ghost_browser_mcp / navigate

Called MCP tool

ghost_browser_mcp / take_screenshot

Called MCP tool

ghost_browser_mcp / get_server_info
{}
{
  "cwd": "/app",
  "platform": "Linux",
  "python": "3.12.13",
  "path_sep": "/",
  "home": "/home/mcpuser",
  "container": true,
  "client_workspace_mount": "/workspace",
  "client_workspace_host_hint": "ghost_browser_mcp_output",
  "output_path_guidance": "In Docker mode, save artifacts under /workspace or pass normal paths like /app/name/file.html; they will be redirected to the client-visible workspace mount. Files in this mounted workspace are user-facing outputs and are not automatically deleted by the server cleanup sweep."
}

Called MCP tool

ghost_browser_mcp / take_screenshot
{
  "instance_id": "084ea4ad-6236-45ac-b3eb-c01673ddf5c4",
  "file_path": "/workspace/govbr_screenshot.png",
  "full_page": false
}
{
  "file_path": "/workspace/govbr_screenshot.png",
  "client_path_hint": "ghost_browser_mcp_output/govbr_screenshot.png",
  "workspace_mount": "/workspace",
  "message": "Screenshot saved. AI agents should use the Read tool to view this image."
}

Called MCP tool

ghost_browser_mcp / save_page_html
{
  "instance_id": "084ea4ad-6236-45ac-b3eb-c01673ddf5c4",
  "output_path": "/workspace/govbr/index.html"
}
{
  "file_path": "/workspace/govbr/index.html",
  "client_path_hint": "ghost_browser_mcp_output/govbr/index.html",
  "workspace_mount": "/workspace",
  "file_size_kb": 318.97,
  "url": "https://www.gov.br/pt-br",
  "selector": null
}

Called MCP tool

ghost_browser_mcp / download_element_assets_to_folder

Called MCP tool

ghost_browser_mcp / take_screenshot
Error(s) while reading file(s)
Command
c:\Users\empresa\Desktop\teste4

Get-ChildItem -Path "C:\Users\empresa\Desktop\teste4" -Recurse -Depth 2 | Select-Object FullName
p\teste4" -Recurse -Depth 2 | Select-Object FullName                            
Command
c:\Users\empresa\Desktop\teste4

Get-ChildItem -Path "C:\Users\empresa\Desktop\teste4" -Force | Select-Object Name, Attributes
p\teste4" -Force | Select-Object Name, Attributes                               
Command
c:\Users\empresa\Desktop\teste4

dir "C:\Users\empresa\Desktop\teste4" /a
PS C:\Users\empresa\Desktop\teste4> dir "C:\Users\empresa\Desktop\teste4" /a
Get-ChildItem: Second path fragment must not be a drive or UNC name. (Parameter 
'expression')
Command
c:\Users\empresa\Desktop\teste4

ls -la
PS C:\Users\empresa\Desktop\teste4> ls -la
Get-ChildItem: A parameter cannot be found that matches parameter name 'la'.
Command
c:\Users\empresa\Desktop\teste4

Get-ChildItem -Force
PS C:\Users\empresa\Desktop\teste4> Get-ChildItem -Force
O workspace está vazio — os arquivos foram salvos dentro do container Docker do Ghost Browser MCP em /workspace, mas não estão mapeados para o workspace local C:\Users\empresa\Desktop\teste4.

Vou agora pegar o HTML completo e os assets e recriar tudo localmente. Primeiro, vou ler o HTML salvo no container e reprocessar para criar o clone localmente.


Called MCP tool

ghost_browser_mcp / get_page_content

Called MCP tool

ghost_browser_mcp / extract_related_files
Agora vou capturar a estrutura DOM completa e construir o clone localmente com os assets referenciados via URLs absolutas.


Called MCP tool

ghost_browser_mcp / execute_script

Called MCP tool

ghost_browser_mcp / execute_script

Called MCP tool

ghost_browser_mcp / execute_script

Called MCP tool

ghost_browser_mcp / execute_script
Agora tenho tudo que preciso. Vou construir o clone localmente — o HTML com todos os CSS e JS referenciados via URLs absolutas (CDN/gov.br), que é a abordagem mais fiel e funcional.


Called MCP tool

ghost_browser_mcp / execute_script
Tenho o HTML completo. Agora vou criar o arquivo index.html no workspace local com o HTML capturado, injetando a <base> tag correta para que todos os recursos relativos apontem para https://www.gov.br/:

Error(s) while creating

index.html

