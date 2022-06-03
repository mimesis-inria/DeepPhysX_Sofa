"""
#01 - Implementing a SofaEnvironment
DummyEnvironment: SOFA compatible version
"""

# Python related imports
from numpy import array

# DeepPhysX related imports
from DeepPhysX.Sofa.Environment.SofaEnvironment import SofaEnvironment


# Create an Environment as a SofaEnvironment child class
class DummyEnvironment(SofaEnvironment):

    def __init__(self,
                 root_node,
                 ip_address='localhost',
                 port=10000,
                 instance_id=1,
                 number_of_instances=1,
                 as_tcp_ip_client=True,
                 environment_manager=None):

        SofaEnvironment.__init__(self,
                                 root_node=root_node,
                                 ip_address=ip_address,
                                 port=port,
                                 instance_id=instance_id,
                                 number_of_instances=number_of_instances,
                                 as_tcp_ip_client=as_tcp_ip_client,
                                 environment_manager=environment_manager)

        self.nb_step = 0
        self.increment = 0

    """
    INITIALIZING ENVIRONMENT - Methods will be automatically called it this order:
       - recv_parameters: Receive a dictionary of parameters that can be set in EnvironmentConfig
       - create: Create the scene graph (add the components and child nodes to root_node)
       - init: Initialize the scene graph (ALREADY IMPLEMENTED)
       - onSimulationInitDoneEvent: SOFA event will trigger this method right after the init call above
       - send_parameters: Same as recv_parameters, Environment can send back a set of parameters if required
       - send_visualization: Send initial visualization data (see Example/CORE/Features to add visualization data)
    """

    # Optional
    def recv_parameters(self, param_dict):
        # Set data size
        self.increment = param_dict['increment'] if 'increment' in param_dict else 1

    # MANDATORY
    def create(self):
        # Add SOFA plugins
        plugins = ['SofaComponentAll']
        self.root.addObject('RequiredPlugin', pluginName=plugins)
        self.root.addChild('object')
        self.root.object.addObject('MechanicalObject', name='MO', position=[0., 0., 0.])

    # Optional
    def onSimulationInitDoneEvent(self, event):
        # Nothing to compute after init
        pass

    # Optional
    def send_parameters(self):
        # Nothing to send back
        return {}

    # Optional
    def send_visualization(self):
        # Nothing to visualize (see Example/CORE/Features to add visualization data)
        return {}

    """
    ENVIRONMENT BEHAVIOR - Methods will be automatically called at each simulation step in this order:
       - step: Transition in simulation state, compute training data (ALREADY IMPLEMENTED)
       - onAnimateBeginEvent: SOFA event will trigger this method at the beginning of the time step
       - onAnimateEndEvent: SOFA event will trigger this method at the end of the time step
       - on_step: Actions to perform after a time step
       - check_sample: Check if current data sample is usable
       - apply_prediction: Network prediction will be applied in Environment
       - close: Shutdown procedure when data producer is no longer used
     Some requests can be performed here:
       - get_prediction: Get an online prediction from an input array
       - update_visualization: Send updated visualization data (see Example/CORE/Features to update viewer data)
    """

    # Optional
    def onAnimateBeginEvent(self, event):
        # Generally set initial conditions for the following time step
        pass

    # Optional
    def onAnimateEndEvent(self, event):
        # Generally compute training data according to the time step
        self.set_training_data(input_array=array([self.nb_step]),
                               output_array=array([self.nb_step]))
        self.nb_step += self.increment
        # Other data fields can be filled:
        #   - set_loss_data: Define an additional data to compute loss value (see Optimization.transform_loss)
        #   - set_additional_dataset: Add a field to the dataset
        pass

    # Optional
    async def on_step(self):
        # Additional stuff to compute after time step
        # WARNING: the 3 above methods are not mandatory but at least one must be defined to compute training data
        # Possibility to perform some requests here:
        #   - get_prediction: Get an online prediction from an input array
        #   - update_visualization: Send updated visualization data (see Example/CORE/Features to update viewer data)
        pass

    # Optional
    def check_sample(self, check_input=True, check_output=True):
        # Nothing to check in our DummyEnvironment
        return True

    # Optional
    def apply_prediction(self, prediction):
        # Nothing to apply in our DummyEnvironment
        print(f"Prediction at step {self.nb_step - self.increment} = {prediction}")

    # Optional
    def close(self):
        # Shutdown procedure
        print("Bye!")
