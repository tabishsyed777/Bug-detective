"""Counterexample-driven debugging of a bundled discount calculator."""
import argparse, ast, json
from engine import Agent, save
BUG = 'price * (1 - percent)'
FIX = 'price * (1 - percent / 100)'
CASES = [(100,20,80),(75,0,75),(50,100,0),(19.99,10,17.991)]

def evaluate(expression):
    if not isinstance(expression,str) or len(expression)>500: raise ValueError('Invalid expression')
    tree = ast.parse(expression,mode='eval').body
    if len(list(ast.walk(tree)))>40: raise ValueError('Expression too complex')
    def calc(node, values):
        if isinstance(node,ast.Constant) and type(node.value) in (int,float): return node.value
        if isinstance(node,ast.Name) and node.id in values: return values[node.id]
        if isinstance(node,ast.BinOp):
            a,b = calc(node.left,values),calc(node.right,values)
            if isinstance(node.op,ast.Add): return a+b
            if isinstance(node.op,ast.Sub): return a-b
            if isinstance(node.op,ast.Mult): return a*b
            if isinstance(node.op,ast.Div): return a/b
        raise ValueError('Only arithmetic over price and percent is supported')
    results=[]
    for price,percent,expected in CASES:
        actual=calc(tree,dict(price=price,percent=percent))
        results.append(dict(price=price,percent=percent,actual=actual,expected=expected,passed=abs(actual-expected)<1e-8))
    return results

def investigate(agent):
    baseline=evaluate(BUG)
    diagnosis=agent.run('Diagnostician: identify the calculation error.',dict(expression=BUG,tests=baseline),
        {'cause':'Percentage must be divided by 100.'})
    feedback, attempts = baseline, []
    for i in range(2):
        candidate=agent.run('Repair agent: return expression, an arithmetic expression using price and percent.',
            dict(expression=BUG,diagnosis=diagnosis,feedback=feedback),{'expression':FIX})
        try:
            results=evaluate(candidate.get('expression'))
            accepted=all(r['passed'] for r in results)
            feedback=results
        except (ValueError,SyntaxError,TypeError,ArithmeticError) as error:
            results,accepted,feedback=[],False,{'error':str(error)}
        attempts.append(dict(candidate=candidate,tests=results,feedback=feedback))
        if accepted: break
    return dict(status='verified_on_bundled_cases' if accepted else 'needs_review',baseline=baseline,diagnosis=diagnosis,attempts=attempts)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true')
    parser.add_argument('--out',default='work/bug-detective')
    args=parser.parse_args()
    agent=Agent(args.live)
    report=investigate(agent)
    save(args.out,report,agent)
    print(json.dumps(report,indent=2))
