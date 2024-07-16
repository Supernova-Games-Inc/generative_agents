import gradio as gr
import os
import json
import subprocess

sim_base_name = 'zora_gradio_25_skip_test'
storage_path = "environment/frontend_server/storage"
sim_path = f"{storage_path}/{sim_base_name}/personas"
meta_file = f"reverie/meta.json"
agent_file_name = 'bootstrap_memory/scratch.json'
script_path = './run_backend_automatic.sh'
agents = {}
all_sims = {}

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
        info = [agent["age"],
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
        check_freq *= 6
        with open(f"{storage_path}/{sim_base_name}/{meta_file}", 'r') as f:
            temp_data = json.load(f)
            curr_step = temp_data["step"]
        print(curr_step)
        path = script_path
        options = [
            '-o', sim_base_name,
            '-t', sim_name,
            '-s', str(curr_step+steps),
            '-c', str(check_freq)
        ]
        command = [path] + options
        print(command)
        # command = ['./run_backend_automatic.sh', '-o', 'skip-morning-s-14', '-t', 'test_gradio', '-s', '3100']
        # Execute the shell script with an argument
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        # print(command)
        return result.stdout # Return stdout and no error

    except subprocess.CalledProcessError as e:
        # If the script execution failed, return None and stderr
        print("error", e)
        return e.stderr

    except Exception as e:
        print(f"An error occurred: {e}")
        return e.stderr

def summary_simulation(sim_name, steps):
    return f"TEMP SUMMARY FOR {sim_name} on steps {steps}"

def delete_simulation(sim_name, steps):
    return f"DELETE SIMULATION FOR {sim_name} on steps {steps}"

def update_step_range(all_sim_names):
    return gr.update(maximum=all_sims[all_sim_names]["step"], interactive=True)

def set_replay(all_sim_names, step):
    replay_link = f'http://localhost:8000/replay/{all_sim_names}/{step}/'
    return [replay_link, gr.update(interactive=True)]

def main():
    global agents, all_sims
    agents = read_json_from_directories(sim_path, agent_file_name)
    all_sims = read_sims_from_directories()

    with gr.Blocks() as demo:
        gr.Markdown("## New Simulation: Select and Update Agent")
        with gr.Row():
            agent_name = gr.Dropdown(list(agents.keys()), label="Select Agent")
            update_button = gr.Button("Update Agent Information", interactive=False)
             
        gr.Markdown("## Agent Details")
        with gr.Column():
            input_age = gr.Number(label="Age")
            input_daily_req = gr.Textbox(label="Daily Plan Requirement")
            input_innate = gr.Textbox(label="Innate")
            input_learned = gr.Textbox(label="Learned")
            input_currently = gr.Textbox(label="Currently")
            input_lifestyle = gr.Textbox(label="Lifestyle")
            input_living_area = gr.Textbox(label="Living Area")
            input_memory =  gr.Textbox(label="Memory")

        with gr.Row():
            sim_name = gr.Text(label="Simulation Name", placeholder = "new_sim")
            sim_start_hour = gr.Number(minimum=0, maximum=24, value = 0, label="Hour")
            sim_start_mins = gr.Number(minimum=0, maximum=59, value = 0, label="Mins")
            sim_check_freq = gr.Number(minimum=15, maximum=120, step=15,label="check_point_freq")
            sim_steps = gr.Number(label="Simulation Steps")
        with gr.Row():
            start_button = gr.Button("Start Simulation!")
            watch_sim_button = gr.Button("Watch Live Simulation",link='http://localhost:8000/simulator_home') 

        std_output = gr.Textbox(label="Running Output")
        sim_result = gr.Textbox(label="Simulation Result")

        gr.Markdown("## Simulation Process")
        with gr.Row():
            summary_button = gr.Button("Get Summary")
            all_agents = gr.Dropdown(list(agents.keys()), multiselect=True, label="Select Agent")
            delete_button = gr.Button("Delete Simulation")

        gr.Markdown("## Simulation Replay")
        with gr.Row():
            all_sim_names = gr.Dropdown(list(all_sims.keys()), label="Select Simulations")
            sim_start_step = gr.Number(minimum=1, maximum=100, value = 1, label="Steps")
            # sim_start_hour = gr.Number(minimum=0, maximum=24, value = 0, label="Hour")
            # sim_start_mins = gr.Number(minimum=0, maximum=59, value = 0, label="Mins")
            step_convert = gr.Number(label="convert")
            new_hour = gr.Number(minimum=0, maximum=24, value = 0, label="New Hour")
            new_mins = gr.Number(minimum=0, maximum=59, value = 0, label="New Mins")
            # speed = gr.Radio(choices=[1,2,3,4,5], value=1, label="Speed")
            sim_replay_button = gr.Button("Watch Simulation Replay", interactive=False)
            link_text = gr.Textbox(label="REPLAY LINK", visible=False)
  
        sim_start_hour.change(time_2_step, inputs = [sim_start_hour, sim_start_mins], outputs=sim_steps)
        sim_start_mins.change(time_2_step, inputs = [sim_start_hour, sim_start_mins], outputs=sim_steps)
        # step_convert.change(step_2_time, inputs = step_convert, outputs=[new_hour, new_mins])


        # all_sim_names.change(enable_buttom, inputs=None, outputs=sim_replay_button)
        agent_name.change(show_agent_info, inputs=[agent_name], outputs=[input_age, input_daily_req, input_innate, input_learned, input_currently, input_lifestyle, input_living_area, update_button])
        all_sim_names.change(update_step_range, inputs=all_sim_names, outputs=[sim_start_step])
        sim_start_step.change(set_replay, inputs=[all_sim_names, sim_start_step], outputs=[link_text, sim_replay_button])

        sim_replay_button.click(fn=None,inputs=link_text , js=f"(link_text) => {{ window.open(link_text, '_blank') }}")


        # sim_replay_button.click(fn=set_replay,inputs=[all_sim_names, sim_start_step], outputs=link_text , js=f"(link_text) => {{ window.open(link_text, '_blank') }}")


        input_list = [input_age, input_daily_req, input_innate, input_learned, input_currently, input_lifestyle, input_living_area, input_memory]     
        # Assign change event to each input to enable update button
        for input_field in input_list:
            input_field.change(enable_buttom, inputs=None, outputs=update_button)

        
        update_button.click(update_agent, inputs=[agent_name, input_age, input_daily_req, input_innate, input_learned, input_currently, input_lifestyle, input_living_area], outputs=[update_button, std_output])
        start_button.click(start_simulation, inputs=[sim_name, sim_steps, sim_check_freq], outputs = std_output)
        summary_button.click(summary_simulation, inputs=[sim_name, sim_steps], outputs = sim_result)
        delete_button.click(delete_simulation, inputs=[sim_name, sim_steps], outputs = sim_result)


    demo.launch(server_port=8005, inbrowser=True, share=True)
    # demo.launch(server_port=8005, share=True,
    #             server_name="0.0.0.0", show_api=False)


if __name__ == "__main__":
    main()
