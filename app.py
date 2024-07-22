import gradio as gr
import os
import json
import subprocess
import datetime
from sorted_key_value_store import SortedKeyValueStore

sim_base_name = 'zora_gradio_25_skip_test'
storage_path = "environment/frontend_server/storage"
sim_path = f"{storage_path}/{sim_base_name}/personas"
meta_file = f"reverie/meta.json"
agent_file_name = 'bootstrap_memory/scratch.json'
script_path = './run_backend_automatic.sh'
agents = {}
all_sims = {}
check_point_map = SortedKeyValueStore()

def time_2_step(hour, mins):
    mins += hour * 60
    steps = mins * 6
    return steps

def step_2_time(steps):
    total_minutes = steps / 6
    hour = int(total_minutes // 60)
    mins = int(total_minutes % 60)
    return hour, mins

def show_agent_info(agent_name):
    if agent_name in agents:
        agent = agents[agent_name]
        info = [agent["name"],
                agent["age"],
                agent["daily_plan_req"],
                agent["innate"],
                agent["learned"],
                agent["currently"],
                agent["lifestyle"],
                agent["living_area"],
                gr.update(interactive=False)
                ]
        return info
    else:
        return "Agent not found. Please add new agent details using the form below."

def update_agent(agent_name, input_age, input_daily_req, input_innate, input_learned, input_currently, input_lifestyle, input_living_area):
    agents[agent_name]["age"] = input_age
    agents[agent_name]["daily_plan_req"] = input_daily_req
    agents[agent_name]["innate"] = input_innate
    agents[agent_name]["learned"] = input_learned
    agents[agent_name]["currently"] = input_currently
    agents[agent_name]["lifestyle"] = input_lifestyle
    agents[agent_name]["living_area"] = input_living_area
    update_json_from_directories(sim_path, agent_file_name)

    return [gr.update(interactive=False), f"Agent '{agent_name}' information update successfully."]

def enable_buttom():
    return gr.update(interactive=True)

def read_json_from_directories(base_path, filename):
        data = {}
        with os.scandir(base_path) as entries:
            for entry in entries:
                if entry.is_dir():
                    file_path = os.path.join(entry.path, filename)
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, 'r') as json_file:
                                data[entry.name] = json.load(json_file)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON from {file_path}: {e}")
                        except Exception as e:
                            print(f"An error occurred while reading {file_path}: {e}")
                    else:
                        print(file_path, os.path.exists(file_path))
        return data

def read_sims_from_directories():
    data = {}
    with os.scandir(storage_path) as entries:
            for entry in entries:
                if entry.is_dir():
                    file_path = os.path.join(entry.path, meta_file)
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, 'r') as json_file:
                                data[entry.name] = json.load(json_file)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON from {file_path}: {e}")
                        except Exception as e:
                            print(f"An error occurred while reading {file_path}: {e}")
                    else:
                        print(file_path, os.path.exists(file_path))
    return data

def update_json_from_directories(base_path, filename):
        # data = {}
        with os.scandir(base_path) as entries:
            for entry in entries:
                if entry.is_dir():
                    file_path = os.path.join(entry.path, filename)
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, 'w') as json_file:
                                json.dump(agents[entry.name], json_file, indent=4)
                                # agents[entry.name] = json.load(json_file)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON from {file_path}: {e}")
                        except Exception as e:
                            print(f"An error occurred while reading {file_path}: {e}")
                    else:
                        print(file_path, os.path.exists(file_path))

def start_simulation(sim_name, steps, check_freq):
    try:
        print("Current Directory:", os.getcwd())
        with open(f"{storage_path}/{sim_base_name}/{meta_file}", 'r') as f:
            temp_data = json.load(f)
            curr_step = temp_data["step"]
        print(curr_step)
        path = script_path
        options = [
            '-o', sim_base_name,
            '-t', sim_name,
            '-s', str(curr_step+steps),
            '-c', str(check_freq*6) # check_freq is mins unit
        ]
        command = [path] + options
        print(command)
        # command = ['./run_backend_automatic.sh', '-o', 'skip-morning-s-14', '-t', 'test_gradio', '-s', '3100']
        # Execute the shell script with an argument
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(result.stdout)
        return gr.update("finished")
        # return result.stdout
        # return [result.stdout,gr.update(interactive=True), gr.update(interactive=True),gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True),gr.update(interactive=True)] # Return stdout and no error
  

    except subprocess.CalledProcessError as e:
        # If the script execution failed, return None and stderr
        print("error", e)
        return e.stderr

    except Exception as e:
        print(f"An error occurred: {e}")
        return e.stderr

def summary_simulation(sim_name, steps):
    return f"TEMP SUMMARY FOR {sim_name} on steps {steps}"

def get_check_point_summary(sim_check_point_time):
    all_agent_name = agents.keys()
    summary = {}
    sim_name = check_point_map.get_key(sim_check_point_time)
    base_path = f"{storage_path}/{sim_name}/personas"
    with os.scandir(base_path) as entries:
        for entry in entries:
            if entry.is_dir() and entry.name in all_agent_name:
                file_path = os.path.join(entry.path, "bootstrap_memory/summary.json")
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as json_file:
                            temp = json.load(json_file)
                            summary[entry.name] = temp["new summary"]
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON from {file_path}: {e}")
                    except Exception as e:
                        print(f"An error occurred while reading {file_path}: {e}")
                else:
                    print(file_path, os.path.exists(file_path))
                    return "Summary is not ready, please wait for the current checkpoint of simulation to finish."
    return format_check_point_summary(summary)

def get_summary(sim_check_point_time, agents):
    if len(agents) < 1:
        return "Please select at least one agents to see the summary details."
    else:
        summary = ""
        sim_name = check_point_map.get_key(sim_check_point_time)
        base_path = f"{storage_path}/{sim_name}/personas"
        with os.scandir(base_path) as entries:
            for entry in entries:
                if entry.is_dir() and entry.name in agents:
                    file_path = os.path.join(entry.path, "bootstrap_memory/summary.json")
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, 'r') as json_file:
                                temp = json.load(json_file)
                                temp_summary = temp["new summary"]
                                summary += entry.name + "\n" + format_summary(temp_summary, 5) + "\n"
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON from {file_path}: {e}")
                        except Exception as e:
                            print(f"An error occurred while reading {file_path}: {e}")
                    else:
                        print(file_path, os.path.exists(file_path))
                        return "Summary is not ready, please wait for the current checkpoint of simulation to finish."
        return summary
    
def dict_2_str(the_dict): 
    result = ""
    for k,v in the_dict.items():
        temp = ""
        for i, each in enumerate(v):
            temp += str(i+1) + " : " + each + "\n"
        result += f" {k} \n {temp} \n"
    return result

def check_point_step_2_time(check_points):
    global check_point_map
    
    for each in check_points:
        pattern = each.split("-")
        print(pattern)
        if each not in check_point_map.get_sorted_keys():
            start_sec, end_sec = int(pattern[3]) * 10, int(pattern[4]) * 10
            start_time = datetime.timedelta(seconds=start_sec)
            end_time = datetime.timedelta(seconds=end_sec)
            # start_hour, start_min = step_2_time(int(pattern[3]))
            # end_hour, end_min = step_2_time(int(pattern[4]))
            name = pattern[0]
            period =  f"{name} [{start_time} -- {end_time}]"
            check_point_map.insert(each, period)
    print(check_point_map)
    # result_key = list(check_point_map.keys())
    # result_key.sort()
    # result_time, result_step = [], []

    # for each in result_key:
    #     result_step.append(check_point_map[each][0])
    #     result_time.append(check_point_map[each][1])

    return check_point_map.get_sorted_keys(), check_point_map.get_sorted_values()

def format_check_point_summary(summary):
    conv_set = set()
    dict_format = {}

    for each_agent in summary:
        for k, v in summary[each_agent]["event"].items():
            if v["predicate"] == "chat with":
                temp_descript = ""
                try:
                    temp_list = v["description"].split("conversing about")[1:]
                    if len(temp_list) > 1:
                        temp_descript = "conversing about".join(temp_list)
                    else:
                        temp_descript = temp_list[0]   
                except:
                    temp_descript = v["description"]
                # print("------")
                # print(temp_descript)
                # print(v["description"])
                # print("------")

                if temp_descript not in conv_set:
                    conv_set.add(temp_descript)
                    if k in dict_format:
                        dict_format[k].append(v["description"])
                    else:
                        dict_format[k] = [v["description"]]

    return dict_2_str(dict_format)

def format_summary(summary, score):
    formated = ''
    for k, v in summary['event'].items():
        if v["poignancy"] >= score:
            if v["predicate"] == "chat with":
                formated += k + "  [ CONVERSATION ] " +  v["description"] + " < " + str(v["poignancy"]) + " > " + "\n"
            else:
                formated += k + "  [ EVENT ] " +  v["description"] + " < " + str(v["poignancy"]) + " > " + "\n"

    for k, v in summary['thought'].items():
        formated += k + "  [ THOUGHT ] " +  v["description"] + "\n"

    return formated

def get_check_point(sim_name):
    global all_sims
    all_sims = read_sims_from_directories()
    folder=[key for key, value in all_sims.items() if key.startswith(sim_name)]
    f1, f2 = check_point_step_2_time(folder)
    return [gr.update(choices=f1, interactive=True), gr.update(choices=f2, interactive=True)]

def delete_simulation(sim_name, steps):
    return f"DELETE SIMULATION FOR {sim_name} on steps {steps}"

def update_step_range(all_sim_names):
    return gr.update(maximum=all_sims[all_sim_names]["step"], interactive=True)

def set_replay(all_sim_names, step):
    replay_link = f'http://localhost:8000/replay/{all_sim_names}/{step}/'
    return [replay_link, gr.update(interactive=True)]

def save_setting(sim_name, sim_check_freq):
    #save_button.click(save_setting, inputs=[sim_name, sim_check_freq], outputs=[new_sim_name, hour, mins, summary_button, save_button, start_button, reset_button])
    return [sim_name,
            gr.update(interactive=True), # summary_button
            gr.update(interactive=False), # save_button
            gr.update(interactive=True), # start_button
            gr.update(interactive=True)] # reset_button

def reset_setting(sim_name, sim_check_freq):
    # reset_button.click(reset_setting, inputs=[sim_name, sim_check_freq], outputs=[sim_name, new_sim_name, summary_button, save_button, start_button, reset_button])
    return ["", "", 0, 0,
            gr.update(interactive=False), # summary_button
            gr.update(interactive=True), # save_button
            gr.update(interactive=False), # start_button
            gr.update(interactive=False)] # reset_button

def main():
    global agents, all_sims
    agents = read_json_from_directories(sim_path, agent_file_name)
    all_sims = read_sims_from_directories()

    with gr.Blocks() as demo:
        #  ---------------- SIMULATION SETTING ------------------------
        gr.Markdown("## Agent Settings: Select and Update Agent Basic Information")
        with gr.Row():
            agent_name = gr.Radio(list(agents.keys()), label="Select Agent")
             
        gr.Markdown("## Agent Details")
        with gr.Column():
            with gr.Row():
                selected_agent_name = gr.Textbox(label="Name", interactive=False)
                update_button = gr.Button("Update Agent Information", interactive=False)
            input_age = gr.Number(label="Age")
            input_daily_req = gr.Textbox(label="Daily Plan Requirement")
            input_innate = gr.Textbox(label="Innate")
            input_learned = gr.Textbox(label="Learned")
            input_currently = gr.Textbox(label="Currently")
            input_lifestyle = gr.Textbox(label="Lifestyle")
            input_living_area = gr.Textbox(label="Living Area")
            input_memory =  gr.Textbox(label="Memory")

        gr.Markdown("## Simulation Settings")
        with gr.Row():
            sim_name = gr.Text(label="New Simulation Name", placeholder="new_sim")
            sim_start_hour = gr.Number(minimum=0, maximum=24, value=0, label="Hour")
            sim_start_mins = gr.Number(minimum=0, maximum=59, value=0, label="Mins")
            sim_check_freq = gr.Number(minimum=10, maximum=120, value=10, step=5, label="Check Point Frequency (mins)")
            sim_steps = gr.Number(label="Simulation Steps")

        with gr.Row():
            save_button = gr.Button("Save")
            reset_button = gr.Button("Reset")
            start_button = gr.Button("Start Simulation!")
            watch_sim_button = gr.Button("Watch Live Simulation",link='http://localhost:8000/simulator_home') 

        std_output = gr.Textbox(label="Running Output")
        sim_result = gr.Textbox(label="Simulation Result")

        input_list = [input_age, input_daily_req, input_innate, input_learned, input_currently, input_lifestyle, input_living_area, input_memory]     
        # Assign change event to each input to enable update button
        for input_field in input_list:
            input_field.change(enable_buttom, inputs=None, outputs=update_button)

        agent_name.change(show_agent_info, inputs=[agent_name], outputs=[selected_agent_name, input_age, input_daily_req, input_innate, input_learned, input_currently, input_lifestyle, input_living_area, update_button])
        update_button.click(update_agent, inputs=[agent_name, input_age, input_daily_req, input_innate, input_learned, input_currently, input_lifestyle, input_living_area], outputs=[update_button, std_output])
        
        sim_start_hour.change(time_2_step, inputs=[sim_start_hour, sim_start_mins], outputs=sim_steps)
        sim_start_mins.change(time_2_step, inputs=[sim_start_hour, sim_start_mins], outputs=sim_steps)

        start_button.click(start_simulation, inputs=[sim_name, sim_steps, sim_check_freq], outputs=[std_output])

        #  ---------------- SIMULATION SUMMARY ------------------------
        gr.Markdown("## Simulation Summary")
        # all_checkpoints = gr.Dropdown(list(all_sims.keys()),label="Select sim checkpoint")
        with gr.Row():
            new_sim_name = gr.Textbox(label="Simulation Name", visible=False)
        with gr.Row():
            all_check_pts_step = gr.Radio(choices=[], label="Select Simulations Check Points")
            all_check_pts_time = gr.Radio(choices=[], label="Select Simulations Check Points")
            summary_button = gr.Button("Refresh Check Point", interactive=False)
            # delete_button = gr.Button("Delete Simulation")
        check_pt_summary = gr.Textbox(label="Check Point Summary", interactive=False)
        selected_agents = gr.CheckboxGroup(list(agents.keys()), label="Select Agent", interactive=False)
        agent_summary_output = gr.Textbox(label="Agent Summary", interactive=False)

        all_check_pts_time.change(get_check_point_summary, inputs=[all_check_pts_time], outputs=[check_pt_summary])

        save_button.click(save_setting, inputs=[sim_name, sim_check_freq], outputs=[new_sim_name, summary_button, save_button, start_button, reset_button])
        reset_button.click(reset_setting, inputs=[sim_name, sim_check_freq], outputs=[sim_name, new_sim_name, sim_start_hour, sim_start_mins, summary_button, save_button, start_button, reset_button])

        new_sim_name.change(get_check_point, inputs=[new_sim_name], outputs =[all_check_pts_step, all_check_pts_time])
        summary_button.click(get_check_point, inputs=[new_sim_name], outputs = [all_check_pts_step, all_check_pts_time])
        # delete_button.click(delete_simulation, inputs=[sim_name, sim_steps], outputs = sim_result)

        all_check_pts_time.change(enable_buttom, inputs=[], outputs=[selected_agents])
        selected_agents.change(get_summary, inputs=[all_check_pts_time, selected_agents], outputs=[agent_summary_output])




         #  ---------------- SIMULATION REPLAY ------------------------
        gr.Markdown("## Simulation Replay")
        with gr.Row():
            all_sim_names = gr.Dropdown(list(all_sims.keys()), label="Select Simulations")
            replay_start_hour = gr.Number(minimum=0, maximum=24, value=0, label="Replay Start Time (Hour)")
            replay_start_mins = gr.Number(minimum=0, maximum=59, value=0, label="Replay Start Time (Mins)")
            sim_replay_step = gr.Number(minimum=1, maximum=100, value=1, label="Steps", interactive=False)
            sim_replay_button = gr.Button("Watch Simulation Replay", interactive=False)
            link_text = gr.Textbox(label="REPLAY LINK", visible=False)

        replay_start_hour.change(time_2_step, inputs=[replay_start_hour, replay_start_mins], outputs=sim_replay_step)
        replay_start_mins.change(time_2_step, inputs=[replay_start_hour, replay_start_mins], outputs=sim_replay_step)
        all_sim_names.change(update_step_range, inputs=all_sim_names, outputs=[sim_replay_step])
        sim_replay_step.change(set_replay, inputs=[all_sim_names, sim_replay_step], outputs=[link_text, sim_replay_button])

        sim_replay_button.click(fn=None,inputs=link_text , js=f"(link_text) => {{ window.open(link_text, '_blank') }}")


    demo.launch(server_port=8005, inbrowser=True, share=True)
    # demo.launch(server_port=8005, share=True,
    #             server_name="0.0.0.0", show_api=False)


if __name__ == "__main__":
    main()
