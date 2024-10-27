import streamlit as st
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes
from htbuilder.units import percent, px


def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))

def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)

def layout(*args):
    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        background_color="#1b1c1d",  # Inverted background color
        color="white",                # Inverted text color
        text_align="center",
        height="auto",
        opacity=1,
        padding=px(20)
    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=px(2),
        color="white"  # Divider color
    )

    body = p()
    foot = div(
        style=style_div
    )(
        hr(style=style_hr),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)
        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)
    
def footer():
    myargs = [
        image('https://idir.uta.edu/sockg/static/img/sockg_logo_transparent.png', width=px(60), height=px(60)),
        br(),
        link("mailto:idirlab@uta.edu", "idirlab.uta.edu"), 
        br(),
        link("https://idir.uta.edu/sockg/terms/", "Terms and Conditions"),
        br(),
        "© 2015-2024 The University of Texas at Arlington. All Rights Reserved."
    ]
    layout(*myargs)