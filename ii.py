import asyncio
import logging
import signal
from vocode.streaming.streaming_conversation import StreamingConversation
from vocode.helpers import create_streaming_microphone_input_and_speaker_output
from vocode.streaming.transcriber import *
from vocode.streaming.agent import *
from vocode.streaming.synthesizer import *
from vocode.streaming.models.transcriber import *
from vocode.streaming.models.agent import *
from vocode.streaming.models.synthesizer import *
from vocode.streaming.models.message import BaseMessage
import vocode

# these can also be set as environment variables
vocode.setenv(
    OPENAI_API_KEY="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",
    DEEPGRAM_API_KEY="c620d0997e3d39104b86bc4da0d613f5e3e5d964",
    AZURE_SPEECH_KEY="8270851de075421cbaadb5719dcb1dba",
    AZURE_SPEECH_REGION="us-east-1",
)


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def main():
    (
        microphone_input,
        speaker_output,
    ) = create_streaming_microphone_input_and_speaker_output(
        use_default_devices=False,
        logger=logger,
        use_blocking_speaker_output=True
    )

    conversation = StreamingConversation(
        output_device=speaker_output,
        transcriber=DeepgramTranscriber(
            DeepgramTranscriberConfig.from_input_device(
                microphone_input,
                endpointing_config=PunctuationEndpointingConfig(),
            )
        ),
        agent=ChatGPTAgent(
            ChatGPTAgentConfig(
                initial_message=BaseMessage(text="What up"),
                prompt_preamble="""The AI is having a pleasant conversation about life""",
            )
        ),
        synthesizer=AzureSynthesizer(
            AzureSynthesizerConfig.from_output_device(speaker_output)
        ),
        logger=logger,
    )
    await conversation.start()
    print("Conversation started, press Ctrl+C to end")
    signal.signal(
        signal.SIGINT, lambda _0, _1: asyncio.create_task(conversation.terminate())
    )
    while conversation.is_active():
        chunk = await microphone_input.get_audio()
        conversation.receive_audio(chunk)


if __name__ == "__main__":
    asyncio.run(main())