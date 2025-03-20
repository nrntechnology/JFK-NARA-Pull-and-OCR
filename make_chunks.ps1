Get-Content D:\repos\JFKdocs\jfk_all.md
for ($i = 0; $i -lt $content.Length; $i += 10000) {
     $chunk = $content[$i..[math]::Min($i+9999, $content.Length-1)]
     $chunk | Out-File PATHTOREPO\JFKdocs\jfk_chunk_$($i/10000+1).md
}