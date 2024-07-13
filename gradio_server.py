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

def start_simulation(sim_name, steps):
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
        ]
        command = [path] + options
        print(command)
        # command = ['./run_backend_automatic.sh', '-o', 'skip-morning-s-14', '-t', 'test_gradio', '-s', '3100']
        # Execute the shell script with an argument
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(command)
        return result.stdout, None  # Return stdout and no error

    except subprocess.CalledProcessError as e:
        # If the script execution failed, return None and stderr
        print("error", e)
        return None, e.stderr

    except Exception as e:
        print(f"An error occurred: {e}")

def update_step_range(all_sim_names):
    return gr.update(maximum=all_sims[all_sim_names]["step"], interactive=True)

def set_replay(all_sim_names, step):
    return gr.update(link=f'http://localhost:8000/replay/{all_sim_names}/{step}/', interactive=True)

def main():
    global agents, all_sims
    agents = read_json_from_directories(sim_path, agent_file_name)
    all_sims = read_sims_from_directories()

    with gr.Blocks() as demo:
        gr.Markdown("## Select or Update an Agent")
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
            sim_steps = gr.Number(label="Simulation Steps")
        with gr.Row():
            start_button = gr.Button("Start Simulation!")
            watch_sim_button = gr.Button("Watch Live Simulation",link='http://localhost:8000/simulator_home')
        

        output_add = gr.Textbox(label="Output")
        sim_result = gr.Textbox(label="simulation_result")

        with gr.Row():
            all_sim_names = gr.Dropdown(list(all_sims.keys()), label="Select Simulations")
            sim_start_step = gr.Number(minimum=1, maximum=100, value = 1, label="Steps")
            # speed = gr.Radio(choices=[1,2,3,4,5], value=1, label="Speed")
            sim_replay_button = gr.Button("Watch Simulation Replay", link=None, interactive=False)
  

        # all_sim_names.change(enable_buttom, inputs=None, outputs=sim_replay_button)
        agent_name.change(show_agent_info, inputs=[agent_name], outputs=[input_age, input_daily_req, input_innate, input_learned, input_currently, input_lifestyle, input_living_area, update_button])
        all_sim_names.change(update_step_range, inputs=all_sim_names, outputs=[sim_start_step])
        sim_start_step.change(set_replay, inputs=[all_sim_names, sim_start_step], outputs=[sim_replay_button])


        input_list = [input_age, input_daily_req, input_innate, input_learned, input_currently, input_lifestyle, input_living_area, input_memory]     
        # Assign change event to each input to enable update button
        for input_field in input_list:
            input_field.change(enable_buttom, inputs=None, outputs=update_button)

        
        update_button.click(update_agent, inputs=[agent_name, input_age, input_daily_req, input_innate, input_learned, input_currently, input_lifestyle, input_living_area], outputs=[update_button, output_add])
        start_button.click(start_simulation, inputs=[sim_name, sim_steps], outputs = sim_result)


    demo.launch(server_port=8005, max_threads=1, inbrowser=True, share=True)
    # demo.launch(server_port=8005, share=True,
    #             server_name="0.0.0.0", show_api=False)


if __name__ == "__main__":
    main()
