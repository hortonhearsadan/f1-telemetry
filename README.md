# f1-telemetry

This is to visualise f1 2019 telemtry data that has bee pre-processed by the f1-2019-telemetry package

#How do i get repeatable data?

Assuming you have setup your F1 2019 game to send the UDP packets, run the following in your terminal

f1-2019-telemetry-recorder 

Then start a f1 session and drive a bit.

Press enter or Ctrl+C to stop the recording

A sqllite file is generated. To replay the session packets do:

f1-2019-telemetry-player RECORDEDFILE

and it will stream your packets, for more info on the cli tools see
https://pypi.org/project/f1-2019-telemetry/
