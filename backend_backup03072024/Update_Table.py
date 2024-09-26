import json

def update_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    for temp_entry in data["temperatures"]:
        for stage_entry in temp_entry["stages"]:
            times = stage_entry["times"]
            stage_entry["times"] = [float(time) if isinstance(time, str) else time for time in times]

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    update_data('Development_Times.json')