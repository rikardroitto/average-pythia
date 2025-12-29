**Projektbeskrivning**



Detta project är ett spel som heter "Average Pythia". Spelets idé att alla som ansluter sig till en spelomgång får:

a) skriva en fråga var där svaret måste vara en siffra. Till frågan kan deltagaren bifoga en bild eller rita en doodle. Som alternativ finns också kurerade frågeserier att välja.

b) svara på varandras frågor, en i taget, synkroniserat, så att spelet väntar in att alla svarat eller maxtiden nåtts

c) Den som gissar median-värdet vinner omgången och får en poäng

d) I slutet utses spelets "Average Pythia",som är den som pricket in flest medianvärden



Spelet är på engelska.



**Tekniska idéer**

Spelets interface ska vara en mobilanpassad websida, så att ingen behöver installera något

Spelet körs som en flask på Render

Eftersom interaktionen sker i realtid behövs websockets

Inloggning via Google Auth

Permanenta data (användares inloggning och kurerade spelomgångar) sparas på Supabase



SPELET STEG FÖR STEG



**Startskärm**



Logga "Average Pythia". Förbered för att visa logo.png och om den inte finns skriv bara ut "Average Pythia"

Spelval:

a) "Start new game"

b)  "Join game"

c)  "Login" (lämnas tom i steg 1, implementeras i steg 2)





**Start new game**



Spelstartaren får ange sitt namn. (Om Spelstartaren är inloggad ska förvalt spelarnamn vara default)

Spelstartaren får också välja mellan "Normal game" eller "Curated questions". (Alternativet "Curated questions" implementeras inte i steg 1 utan i steg 2)



När Spelstartaren angett sitt namn startar ett spel och spelaren kommer till skärmen "Invite"



**Invite**



Här syns

a) en QR-kod för direktanslutning till spelet. Den leder till "Join game, player name" för aktuellt spel

b) en unik kod för den som vill skriva in kod för hand under "Join game"

c) en lista på anslutna spelare

d) en knapp, "Start playing"



När spelstartaren Trycker på "Start playing" hamnar alla spelare som anslutit sig på skärmen "Enter question" om det är ett "Normal game". Om det är ett "Curated questions" game så kommer spelarna direct till första "Answer question"



**Join game**



Här kan spelaren ansluta sig till ett spel genom att skriva in en unik kod för hand

knapp "Join"



**Join game, player name**



Spelaren får skriva in ett namn, som inte får vara samma som någon spelare som redan anslutit sig.

När Spelaren trycker "Confirm" hamnar den på skärmen "Game lobby 1"



**Game lobby 1**



Spelare som ansluter sig får meddelandet "Waiting for players to join"

En lista med vilka som joinat syns.



När spelstartaren trycker på "Start playing" hamnar spelarna på "Enter question"



**Enter question**



a) Text: "Enter question. Answer must be a number"

b) En kvadratisk doodle-ruta där spelarna kan rita med fingret.

c) Knapp "Reset doodle" som gör doodle blank

d) Knapp "upload image" (lämnas tom i steg 1, implementeras i steg 2)

e) En textruta där de kan skriva in sin fråga

f) Knapp "Submit". Knappen fungerar bara om e) inte är tom





När spelstartaren trycker på submit hamnar hen i "Game lobby 2"

När spelare trycker "submit" hamnar de i "Game lobby 3"



**Game lobby 2**



När spelstartaren skickat in sin fråga hamnar han på en skärm:

a)  meddelande "Waiting for players to submit question"

b) En lista med vilka som är klara syns.

c) Knapp: "Start playing". Spelstartaren kan forcera start även om inte alla skrivit in en fråga.





När spelstartaren trycker på "Start playing" händer följande:

a) en ordning för inskickade frågor slumpas fram

 hamnar alla spelarna på "Reply to question".



**Game lobby 3**



Spelare som skickat in sin fråga sig får meddelandet "Waiting for players to submit question"

En lista med vilka som är klara syns.



När spelstartaren trycker på "Start playing" hamnar spelarna på "Reply to question". Spelstartaren kan forcera start.



**Reply to question**



Alla spelare får se bild, doodle och fråga för en av användarnas inskickde frågor

Alla spelare får skriva in en siffra som svar. Endast siffror och punkt (för decimaltal) är tillåten input

Knapp: "submit". Den fungerar bara om spelaren skrivit ett siffersvar.

När spelstartaren tryckt "submit" hamnar hen i "Game lobby 4"

När övriga spelare tryckt "submit" hamnar hen i "Game lobby 5"



**Game lobby 4**



När spelstartaren skickat in sitt svar på en fråga hamnar han på en skärm:

a)  meddelande "Waiting for players to submit reply"

b) En lista med vilka som är klara syns.

c) Knapp: "Present winner". Spelstartaren kan forcera start även om inte alla svarat. När knappen trycks in hamnar alla spelare på "Present Winner"



**Game lobby 5**



Spelare som skickat in sin fråga sig får meddelandet "Waiting for players to submit reply"

En lista med vilka som är klara syns.



När spelstartaren trycker på knappen "Present winner" hamnar spelarna på ""Present winner". Spelstartaren kan forcera progress.



**Present winner**



Här listas alla spelares svar från det lägsta till det högsta. Vinnaren, alltså den spelare som skrivit mediansvaret, är markerad med fetstil och en stjärnemoji.

Om flera spelare gissat mediansvaret är alla vinnare.

Om antalet spelare är jämnt är medianen medel av de två mittersta svaren. I så fall avgörs rätt svar och vinnare enligt följande regler:

a) om ett av de två mittersta svaren ligger närmare medelvärdet av samtliga svar är detta svar vinnarsvaret

b) om de två mittersta svaren ligger exakt lika nära medelvärdet av samtliga svar är båda svaren vinnarsvar

c) samtliga spelare som gissat det svar eller de två svar som utsetts till rätt svar i steg a och b räknas som vinnare

Vinnaren eller vinnarna får 1 poäng var



När spelstartaren trycker på "Next" händer följande:

Om alla frågor besvararats hamnar alla spelarna på "Final results", annars hamnar alla på "Leaderboard"



**Leaderboard**



Rubrik: "Pythia Leaderboard"

Här presenteras totalpoängen för varje spelare hittills i spelet, sorterat i poängordning.



När spelstartaren trycker på "Next" händer hamnar alla på "Reply to question" och får svara på nästa fråga.





**Final results**

Rubrik "Power Pythias"

Här presenteras totalpoängen för alla spelare, sorterat i poängordning. Medaljemojis för de tre första. (Hantera att flera personer kan hamna på samma poäng.)



Knapp längst ned: "Back to start" tar den som trycker till startskärmen. Alla spelare kan trycka på knappen när de vill.



**Curated questions**



(Implementeras i steg 2)





