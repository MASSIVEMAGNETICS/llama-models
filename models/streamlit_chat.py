# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# top-level folder for each specific model found within the models/ directory at
# the top-level of this source tree.

"""Simple Streamlit chat GUI for Llama models."""

from typing import List, Optional

import streamlit as st

from models.datatypes import RawMessage
from models.llama4.generation import Llama4


def load_generator(
    checkpoint_dir: str,
    *,
    max_seq_len: int,
    max_batch_size: int,
    world_size: Optional[int],
    quantization_mode: Optional[str],
):
  return Llama4.build(
      checkpoint_dir,
      max_seq_len=max_seq_len,
      max_batch_size=max_batch_size,
      world_size=world_size,
      quantization_mode=quantization_mode,
  )


st.set_page_config(page_title="Llama Chat", layout="wide")

if "generator" not in st.session_state:
  st.session_state.generator = None
  st.session_state.messages: List[RawMessage] = []

with st.sidebar:
  st.header("Model Parameters")
  checkpoint_dir = st.text_input("Checkpoint directory", "./checkpoints")
  max_seq_len = st.number_input("Max sequence length", 1, 8192, 4096)
  max_batch_size = st.number_input("Max batch size", 1, 16, 1)
  world_size = st.number_input("World size", 1, 1, 1)
  temperature = st.slider("Temperature", 0.0, 1.5, 0.6, 0.1)
  top_p = st.slider("Top p", 0.0, 1.0, 0.9, 0.05)
  quantization_mode = st.selectbox(
      "Quantization mode",
      [None, "int4_mixed", "fp8_mixed"],
      format_func=lambda x: "None" if x is None else x,
  )
  if st.button("Load model"):
    with st.spinner("Loading model..."):
      st.session_state.generator = load_generator(
          checkpoint_dir,
          max_seq_len=max_seq_len,
          max_batch_size=max_batch_size,
          world_size=world_size,
          quantization_mode=quantization_mode,
      )

st.title("Llama Chat")

for msg in st.session_state.messages:
  st.chat_message(msg.role).write(msg.content)

prompt = st.chat_input("Your message")
if prompt:
  st.session_state.messages.append(RawMessage(role="user", content=prompt))
  st.chat_message("user").write(prompt)
  generator = st.session_state.generator
  if generator is None:
    st.error("Model not loaded")
  else:
    dialog = [[m for m in st.session_state.messages]]
    output = ""
    for token in generator.chat_completion(
        dialog,
        temperature=temperature,
        top_p=top_p,
        max_gen_len=max_seq_len,
    ):
      result = token[0]
      if result.finished:
        break
      output += result.text
      st.chat_message("assistant").write(output)
    st.session_state.messages.append(
        RawMessage(role="assistant", content=output)
    )
