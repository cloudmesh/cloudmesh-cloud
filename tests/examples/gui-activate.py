import PySimpleGUI as gui
from cloudmesh.common.console import Console
from cloudmesh.configuration.Config import Config

config = Config()

clouds = list(config["cloudmesh.cloud"].keys())

gui.SetOptions(text_justification='right')

layout = [
    [gui.Text('Cloudmesh Cloud Activation', font=('Helvetica', 16))],
    [gui.Text('Compute Services')]]

layout.append([gui.Text('_' * 100, size=(65, 1))])

for cloud in clouds:
    tbd = "TBD" in str(config[f"cloudmesh.cloud.{cloud}.credentials"])
    active = config[f"cloudmesh.cloud.{cloud}.cm.active"]
    if tbd:
        color = 'red'
    else:
        color = "green"

    choice = [gui.Checkbox(cloud,
                           text_color=color,
                           default=active)]
    layout.append(choice)

layout.append([gui.Text('_' * 100, size=(65, 1))])

layout.append([gui.Submit(), gui.Cancel()])

window = gui.Window('Cloudmesh Configuration', layout, font=("Helvetica", 12))

event, values = window.Read()

selected = []
for i in range(0, len(clouds)):
    cloud = clouds[i]
    if values[i]:
        selected.append(cloud)
        Console.ok(f"Activate Cloud {cloud}")

for cloud in clouds:
    active = False
    if cloud in selected:
        active = True
    config[f"cloudmesh.cloud.{cloud}.cm.active"] = str(active)

config.save()
