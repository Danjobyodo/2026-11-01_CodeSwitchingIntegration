"""Run the standalone comparison notebook headlessly; never runs Monte Carlo."""
import argparse, json, os, hashlib, importlib.metadata, platform
from pathlib import Path

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--n-boot',type=int,default=200)
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    os.chdir(args.output_dir.resolve())
    ns={'__name__':'v92_comparison_run'}
    notebook_path=Path(__file__).with_name('noisy_cost_comparison.ipynb')
    notebook=json.loads(notebook_path.read_text())
    manifest=dict(notebook_sha256=hashlib.sha256(notebook_path.read_bytes()).hexdigest(),
        n_boot=args.n_boot,python=platform.python_version(),
        versions={name:importlib.metadata.version(name) for name in ['numpy','scipy','pandas','stim','pymatching','mpmath']})
    Path('execution_manifest.json').write_text(json.dumps(manifest,indent=2))
    for i,cell in enumerate(notebook['cells']):
        if cell['cell_type']!='code':continue
        source=''.join(cell['source'])
        if 'N_BOOT = 200' in source:source=source.replace('N_BOOT = 200',f'N_BOOT = {args.n_boot}')
        print(f'Executing comparison cell {i}',flush=True)
        exec(compile(source,f'comparison-cell-{i}','exec'),ns)
    print('COMPARISON PASSED',flush=True)
if __name__=='__main__':main()
