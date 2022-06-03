"""
validation.py
Launch the prediction session in a SOFA GUI. Compare the two models.
Use 'python3 validation.py -e' to run the pipeline with newly created samples in Environment (default).
Use 'python3 validation.py -d' to run the pipeline with existing samples from a Dataset.
"""

# Python related imports
import os
import sys

# Sofa related imports
import Sofa.Gui

# DeepPhysX related imports
from DeepPhysX.Core.Dataset.BaseDatasetConfig import BaseDatasetConfig
from DeepPhysX.Sofa.Pipeline.SofaRunner import SofaRunner
from DeepPhysX.Torch.FC.FCConfig import FCConfig
from DeepPhysX.Sofa.Environment.SofaEnvironmentConfig import SofaEnvironmentConfig

# Session related imports
from download import BeamDownloader
from Environment.BeamValidation import BeamValidation, p_grid


def create_runner(dataset_dir):

    # Environment config
    env_config = SofaEnvironmentConfig(environment_class=BeamValidation,
                                       param_dict={'compute_sample': dataset_dir is None},
                                       as_tcp_ip_client=False)

    # FC config
    nb_hidden_layers = 2
    nb_neurons = p_grid.nb_nodes * 3
    layers_dim = [nb_neurons] + [nb_neurons for _ in range(nb_hidden_layers + 1)] + [nb_neurons]
    net_config = FCConfig(network_name='beam_FC',
                          dim_output=3,
                          dim_layers=layers_dim,
                          biases=True)

    # Dataset config
    dataset_config = BaseDatasetConfig(shuffle_dataset=True,
                                       normalize=True,
                                       dataset_dir=dataset_dir,
                                       use_mode=None if dataset_dir is None else 'Validation')

    # Define trained network session
    dpx_session = 'beam_dpx'
    user_session = 'beam_training_user'
    # Take user session by default
    session_name = user_session if os.path.exists('sessions/' + user_session) else dpx_session

    # Runner
    return SofaRunner(session_dir='sessions',
                      session_name=session_name,
                      dataset_config=dataset_config,
                      environment_config=env_config,
                      network_config=net_config,
                      nb_steps=500)


if __name__ == '__main__':

    # Define dataset
    dpx_session = 'sessions/beam_dpx'
    user_session = 'sessions/beam_data_user'
    # Take user dataset by default
    dataset = user_session if os.path.exists(user_session) else dpx_session

    # Get option
    if len(sys.argv) > 1:

        # Check script option
        if sys.argv[1] != '-e':
            print("Script option must be '-e' for samples produced in Environment(s)."
                  "Without option, samples are loaded from an existing Dataset.")
            quit(0)
        dataset = None

    # Check missing data
    session_name = 'valid' if dataset is None else 'valid_data'
    BeamDownloader().get_session(session_name)

    # Create SOFA runner
    runner = create_runner(dataset)

    # Launch SOFA GUI
    Sofa.Gui.GUIManager.Init("main", "qglviewer")
    Sofa.Gui.GUIManager.createGUI(runner.root, __file__)
    Sofa.Gui.GUIManager.SetDimension(1080, 1080)
    Sofa.Gui.GUIManager.MainLoop(runner.root)
    Sofa.Gui.GUIManager.closeGUI()

    # Manually close the runner (security if stuff like additional dataset need to be saved)
    runner.close()

    # Delete unwanted files
    for file in os.listdir(os.path.dirname(os.path.abspath(__file__))):
        if '.ini' in file or '.log' in file:
            os.remove(file)
