import PySimpleGUI as sg
from cloudmesh.configuration.Config import Config
from pprint import pprint
from cloudmesh.common.console import Console

config = Config()

clouds = list(config["cloudmesh.cloud"].keys())

pprint (clouds)

sg.SetOptions(text_justification='right')

layout = [
    [sg.Text('Cloudmesh Cloud Activation', font=('Helvetica', 16))],
    [sg.Text('Compute Services')]]

layout.append([sg.Text('_'  * 100, size=(65, 1))])

for cloud in clouds:
    active = config[f"cloudmesh.cloud.{cloud}.cm.active"]
    choice = [sg.Checkbox(cloud, default=active)]
    layout.append(choice)

layout.append([sg.Text('_'  * 100, size=(65, 1))])


layout.append([sg.Submit(), sg.Cancel()])

window = sg.Window('Cloudmesh Configuration', layout, font=("Helvetica", 12))

event, values = window.Read()


selected = []
for i in range(0,len(clouds)):
    cloud = clouds[i]
    if values[i]:
        selected.append(cloud)
        Console.ok("Activate Cloud {cloud}")

for cloud in clouds:
    active = False
    if cloud in selected:
        active = True
    config[f"cloudmesh.cloud.{cloud}.cm.active"] = str(active)

config.save()
