import streamlit as st
import pandas as pd
from multivector_simulator.views.view import UserInput, title_multivettore


def Simulator_Multivettore():
    title_multivettore()

    user_input = UserInput()
    consumption = user_input.download_upload_consumption()
