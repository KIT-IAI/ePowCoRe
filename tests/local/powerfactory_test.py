import os
import sys


PF_ROOT = r"C:\Program Files\DIgSILENT\PowerFactory 2023 SP2"
PF_PY = r"C:\Program Files\DIgSILENT\PowerFactory 2023 SP2\Python\3.10"


sys.path.append(PF_PY)
os.environ["PATH"] = PF_ROOT + ";" + os.environ["PATH"]


import powerfactory as pf


app = pf.GetApplicationExt()
app.Show()


user = app.GetCurrentUser()
app.ActivateProject("14 Bus System")


study_folder = app.GetProjectFolder("study")
case = study_folder.GetContents("01 - Load Flow Case Original Grid.IntCase")[0]
case.Activate()


ldf = app.GetFromStudyCase("ComLdf")
ldf.Execute()


buses = app.GetCalcRelevantObjects("*.ElmTerm")
lines = app.GetCalcRelevantObjects("*.ElmLne")


print("Buses:", len(buses))
print("Lines:", len(lines))


for bus in buses[:5]:
    print(bus.loc_name, bus.GetAttribute("m:u"))


for line in lines[:5]:
    print(line.loc_name, line.GetAttribute("m:loading"))