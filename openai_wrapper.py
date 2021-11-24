import openai
from loguru import logger


def update_api_key(api_key):
    logger.debug("Setting openAI API key to: {0}".format(api_key))
    openai.api_key = api_key

async def completion(prompt, engine="ada", max_tokens=64, temperature=0.7, top_p=1, stop=None, presence_penalty=0, frequency_penalty=0, echo=False, n=1, stream=False, logprobs=None, best_of=1, logit_bias={}):
    logger.debug("Calling GPT-3 for completion of prompt: {0}".format(prompt))
    response = openai.Completion.create(engine=engine,
                                        prompt=prompt,
                                        max_tokens=max_tokens,
                                        temperature=temperature,
                                        top_p=top_p,
                                        presence_penalty=presence_penalty,
                                        frequency_penalty=frequency_penalty,
                                        echo=echo,
                                        stop=stop,
                                        n=n,
                                        stream=stream,
                                        logprobs=logprobs,
                                        best_of=best_of,
                                        logit_bias=logit_bias)
    logger.debug("Received response: {0}".format(response))
    return response


async def search(q, docs, engine="ada"):

    logger.debug("Calling openAI to peform a semantic search for {0} in documents: {1}".format(q, docs))
    response = openai.Engine(engine).search(
        documents=docs,
        query=q
    )
    return response

