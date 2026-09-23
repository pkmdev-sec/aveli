"""Aveli chooses an observed action. Code owns execution."""

__all__ = ["Agent", "Browser", "JobSpec", "ProductionRunner"]


def __getattr__(name):
    if name == "Agent":
        from .agent import Agent

        return Agent
    if name == "Browser":
        from .browser import Browser

        return Browser
    if name == "JobSpec":
        from .job import JobSpec

        return JobSpec
    if name == "ProductionRunner":
        from .runner import ProductionRunner

        return ProductionRunner
    raise AttributeError(name)
