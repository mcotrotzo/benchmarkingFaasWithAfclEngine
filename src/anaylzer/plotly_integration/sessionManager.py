import streamlit as st
class SessionManger:
    
    def __init__(self,key,default_value) -> None:
        self.key = key
        self.default_value=default_value
    
    def set_state(self,value):
        st.session_state[self.key] = value
            
            
    def get_state_func(self):
        if self.key not in st.session_state:
            st.session_state[self.key] = self.default_value
            
        return lambda: st.session_state[self.key]   