from HARK.ConsumptionSaving.ConsPortfolioModel import SequentialPortfolioConsumerType
from sharkfin.broker import *
from sharkfin.expectations import *
from sharkfin.population import *
from sharkfin.simulation import *
from simulate.parameters import (
    agent_population_params,
    approx_params,
    continuous_dist_params,
)
import numpy as np

def build_population(agent_type, parameters, rng = None, dphm = 2000):
    pop = AgentPopulation(agent_type(), parameters, rng = rng, dollars_per_hark_money_unit = dphm)
    pop.approx_distributions(approx_params)
    pop.parse_params()

    pop.create_distributed_agents()
    pop.create_database()
    pop.solve_distributed_agents()

    pop.solve(merge_by=["RiskyAvg", "RiskyStd"])

    # initialize population model
    pop.init_simulation()

    return pop

## MARKET SIMULATIONS

def test_market_simulation():
    """
    Sets up and runs a MarketSimulation with no population.
    """

    # arguments to Calibration simulation

    q = 1
    r = 60
    market = None

    sim = MarketSimulation(q=q, r=r, market=market)
    sim.simulate(burn_in=2)

    data = sim.data()

    assert len(data["prices"]) == 60


def test_calibration_simulation():
    """
    Sets up and runs an agent population simulation
    """
    # arguments to Calibration simulation

    q = 1
    r = 1
    market = None

    sim = CalibrationSimulation(q=q, r=r, market=market)
    sim.simulate(burn_in=2, buy_sell_shock=(200, 600))

    assert sim.broker.buy_sell_history[1] == (0, 0)
    # assert(len(sim.history['buy_sell']) == 3) # need the padded day
    data = sim.data()

    assert len(data["prices"]) == 2

def test_series_simulation():
    """
    Sets up and runs an agent population simulation
    """

    # arguments to Calibration simulation

    q = 1
    r = 1
    market = None

    sim = SeriesSimulation(q=q, r=r, market=market)
    sim.simulate(burn_in=2, series=[(10000, 0), (10000, 0), (10000, 0), (10000, 0), (0,10000), (0, 10000), (0, 10000), (0, 10000)])

    assert sim.broker.buy_sell_history[2] == (10000, 0)
    # assert(len(sim.history['buy_sell']) == 3) # need the padded day
    data = sim.data()

    assert len(data["prices"]) == 9


## MACRO SIMULATIONS

def test_macro_simulation():
    """
    Sets up and runs an simulation with an agent population.
    """
    parameter_dict = agent_population_params | continuous_dist_params
    parameter_dict["AgentCount"] = 1

    # initialize population
    pop = build_population(
        SequentialPortfolioConsumerType,
        parameter_dict,
        rng = np.random.default_rng(1)
        )

    # arguments to attention simulation

    #a = 0.2
    q = 1
    r = 30
    market = None

    days_per_quarter = 30

    attsim = MacroSimulation(
        pop,
        FinanceModel,
        #a=a,
        q=q,
        r=r,
        market=market,
        days_per_quarter=days_per_quarter,
    )
    attsim.simulate(burn_in=20)

    ## testing for existence of this class stat
    attsim.pop.class_stats()["mNrm_ratio_StE_mean"]

    attsim.data()["sell_macro"]

    attsim.sim_stats()

    assert attsim.days_per_quarter == days_per_quarter
    assert attsim.fm.days_per_quarter == days_per_quarter

    data = attsim.data()

    assert len(data["prices"]) == 30

def test_attention_simulation():
    """
    Sets up and runs an agent population simulation
    """
    parameter_dict = agent_population_params | continuous_dist_params
    parameter_dict["AgentCount"] = 1

    # initialize population
    pop = build_population(
        SequentialPortfolioConsumerType,
        parameter_dict,
        rng = np.random.default_rng(1)
        )


    # arguments to attention simulation

    a = 0.2
    q = 1
    r = 1
    market = None

    days_per_quarter = 30

    attsim = AttentionSimulation(
        pop,
        FinanceModel,
        a=a,
        q=q,
        r=r,
        market=market,
        days_per_quarter=days_per_quarter,
    )
    attsim.simulate(burn_in=20)

    ## testing for existence of this class stat
    attsim.pop.class_stats()["mNrm_ratio_StE_mean"]

    attsim.data()["sell_macro"]

    attsim.sim_stats()

    assert attsim.days_per_quarter == days_per_quarter
    assert attsim.fm.days_per_quarter == days_per_quarter

    data = attsim.data()

    assert len(data["prices"]) == 30
