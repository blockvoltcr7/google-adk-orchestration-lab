# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.agents import (
    ConsultationAgentBuilder,
    FitnessOnboardingAgentBuilder,
    IntakeAgentBuilder,
    WelcomeAgentBuilder,
)
from app.prompts import YamlPromptLoader
from app.tools import (
    create_booking_link,
    send_welcome_email,
    validate_client_intake,
)

MODEL = "gemini-3.6-flash"

_model = Gemini(
    model=MODEL,
    retry_options=types.HttpRetryOptions(attempts=3),
)
_prompt_loader = YamlPromptLoader()
_intake_builder = IntakeAgentBuilder(
    model=_model,
    prompt_loader=_prompt_loader,
    validation_tool=validate_client_intake,
)
_consultation_builder = ConsultationAgentBuilder(
    model=_model,
    prompt_loader=_prompt_loader,
)
_welcome_builder = WelcomeAgentBuilder(
    model=_model,
    prompt_loader=_prompt_loader,
    booking_tool=create_booking_link,
    email_tool=send_welcome_email,
)

root_agent = FitnessOnboardingAgentBuilder(
    intake_builder=_intake_builder,
    consultation_builder=_consultation_builder,
    welcome_builder=_welcome_builder,
).build()

app = App(
    root_agent=root_agent,
    name="app",
)
