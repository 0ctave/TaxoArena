foreach($f in $args){ $p = Join-Path 'Z:\FAC\TUBerlin\THESIS\TaxoArena' $f; try { $s=[IO.File]::Open($p,'Open','Read','None'); $s.Close(); "FREE $f" } catch { "BUSY $f : " + $_.Exception.Message } }
