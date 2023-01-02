from typing import Tuple
import numpy as np

from ReplenishmentEnv.env.agent_states import AgentStates

"""
    reward1: calculate the cost when buy in.
    agent_states: object for AgentStates to save all agents info in current env step.
    profit_info: env state. For reward1, following keys are needed:
        - unit_storage_cost: unit storage cost per volume.
"""
def reward1(agent_states: AgentStates, profit_info: dict) -> Tuple[np.array, dict]:
    selling_price      = agent_states["all_facilities", "selling_price"]
    procurement_cost   = agent_states["all_facilities", "procurement_cost"]
    sale               = agent_states["all_facilities", "sale"]
    replenish          = agent_states["all_facilities", "replenish"]
    unit_order_cost    = agent_states["all_facilities", "unit_order_cost"]
    in_stocks          = agent_states["all_facilities", "in_stock"]
    volume             = agent_states["all_facilities", "volume"]
    basic_holding_cost = agent_states["all_facilities", "basic_holding_cost"]
    demand             = agent_states["all_facilities", "demand"]
    backlog_ratio      = agent_states["all_facilities", "backlog_ratio"]
    unit_storage_cost  = np.tile(np.array(profit_info.get("unit_storage_cost", 0.01)).reshape(-1,1), [1, volume.shape[-1]])

    # TODO: discuss whether to add (1 - excess_ratio) * excess as compensation
    income       = selling_price * sale
    outcome      = procurement_cost * replenish
    order_cost   = unit_order_cost * np.where(replenish > 0, 1, 0)
    holding_cost = (basic_holding_cost + unit_storage_cost * volume) * in_stocks
    backlog_cost = (selling_price - procurement_cost) * (demand - sale) * backlog_ratio

    reward       = income - outcome - order_cost - holding_cost - backlog_cost
    reward_info = {
        "reward":       reward,
        "income":       income,
        "outcome":      outcome,
        "order_cost":   order_cost,
        "holding_cost": holding_cost,
        "backlog_cost": backlog_cost,
    }

    return reward_info

"""
    reward2: calculate the cost when sale.
    agent_states: object for AgentStates to save all agents info in current env step.
    profit_info: env state. For reward2, following keys are needed:
        - excess_ratio: Only excess_ratio of excess skus will cost loss in profit
        - unit_storage_cost: unit storage cost per volume.
"""
def reward2(agent_states: AgentStates, profit_info: dict) -> Tuple[np.array, dict]:
    selling_price      = agent_states["all_facilities", "selling_price"]
    procurement_cost   = agent_states["all_facilities", "procurement_cost"]
    sale               = agent_states["all_facilities", "sale"]
    excess             = agent_states["all_facilities", "excess"]
    excess_ratio       = agent_states["all_facilities", "excess_ratio"]
    replenish          = agent_states["all_facilities", "replenish"]
    unit_order_cost    = agent_states["all_facilities", "unit_order_cost"]
    in_stocks          = agent_states["all_facilities", "in_stock"]
    demand             = agent_states["all_facilities", "demand"]
    volume             = agent_states["all_facilities", "volume"]
    basic_holding_cost = agent_states["all_facilities", "basic_holding_cost"]
    backlog_ratio      = agent_states["all_facilities", "backlog_ratio"]
    unit_storage_cost  = np.tile(np.array(profit_info.get("unit_storage_cost", 0.01)).reshape(-1,1), [1, volume.shape[-1]])

    profit       = sale * (selling_price - procurement_cost)
    excess_cost  = procurement_cost * excess * excess_ratio
    order_cost   = unit_order_cost * np.where(replenish > 0, 1, 0)
    holding_cost = (basic_holding_cost + unit_storage_cost * volume) * in_stocks
    backlog_cost = (selling_price - procurement_cost) * (demand - sale) * backlog_ratio
    backlog_cost = np.where(backlog_cost > 0, backlog_cost, 0)



    reward      = profit - excess_cost - order_cost - holding_cost - backlog_cost
    reward_info = {
        "reward":       reward,
        "profit":       profit,
        "excess_cost":  excess_cost,
        "order_cost":   order_cost,
        "holding_cost": holding_cost,
        "backlog_cost": backlog_cost,
    }

    return reward_info