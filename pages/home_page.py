import dash
from home_layout import layout_main

dash.register_page(__name__, path="/home")

layout = layout_main()
