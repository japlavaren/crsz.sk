## About

[www.crsz.sk](www.crsz.sk) is terrible Slovak database of chipped animals. 
It cost tens of thousands euros and it is slow, uneasy to use and has major safety issues...
Of course it does not provide all necessary functionality, so needed tasks I did myself using their api.    

I needed to record many vaccinations after public mass rabies vaccination. 
All vaccination records in this case are same, you just need to repeat same task for every animal again and again. 
In original SW there is not such functionality, and doing this manually will take many hours of pain and swearing.  
If you have TXT file containing all chip numbers of vaccinated animals from chip scanner, with this tool 
you can create vaccination record for each of them in a seconds (instead of minutes using manually original SW).

## Setup
`virtualenv venv && source venv/bin/activate && pip install -r requirements.txt`

# Usage
- Copy TXT file containing chip numbers to this project (one chip number per line).
- `python main.py username password YYYY-MM-DD Dyntec "Canvac R" 181020 numbers.txt` 
