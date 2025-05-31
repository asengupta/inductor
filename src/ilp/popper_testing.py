from popper.util import Settings
from popper.loop import learn_solution

settings = Settings(kbpath='ilp/ilp4', debug=False, noisy=False, max_rules=5)
prog, score, stats = learn_solution(settings)
if prog != None:
    settings.print_prog_score(prog, score)
