$folder_name=1
New-Item -ItemType Directory -Path "C:\Users\admin\Desktop\test\$folder_name"
for ($i=1; $i -le 5000; $i++)
{
  if ($i % 100 -eq 0)
  {
    $folder_name++
    New-Item -ItemType Directory -Path "C:\Users\admin\Desktop\test\$folder_name"
  }
  $folder_path="C:\Users\admin\Desktop\test\$folder_name"
  Copy-Item "C:\Users\admin\Desktop\test\test.pdf" "$folder_path\$i.pdf"
  Write-Host $i
}