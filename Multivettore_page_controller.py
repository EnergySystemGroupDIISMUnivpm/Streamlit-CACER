import streamlit as st
import pandas as pd
from multivector_simulator.views.view import UserInput, UserOuput, title_multivettore
import numpy as np

def Simulator_Multivettore():
    title_multivettore()

    user_input = UserInput()
    consumption = user_input.download_upload_consumption()
    user_output = UserOuput()
    user_output.see_coverage_energy_plot(np.array([1,6,8,9,4]), np.array([1,6,7,8,2]))

