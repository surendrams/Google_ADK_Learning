import gym

gym.envs.registration.register(
    id="WebAgentTextEnv-v0",
    entry_point=(
        "personalized_shopping.shared_libraries.web_agent_site.envs.web_agent_text_env:WebAgentTextEnv"
    ),
)


def init_env(num_products):
    env = gym.make(
        "WebAgentTextEnv-v0",
        observation_mode="text",
        num_products=num_products,
    )
    return env


num_product_items = 50000
_webshop_env = None


def get_webshop_env():
    """Lazy-load the webshop environment on first access."""
    global _webshop_env
    if _webshop_env is None:
        _webshop_env = init_env(num_product_items)
        _webshop_env.reset()
        print(f"Finished initializing WebshopEnv with {num_product_items} items.")
    return _webshop_env
