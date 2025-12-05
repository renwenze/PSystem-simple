def record(log):
    import os 
    from datetime import datetime
    import json
 
    now = datetime.now()
 
    time_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    directory = 'log'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename =time_string + ".json"
    if os.path.exists(f'log/{filename}'):
        os.remove(f'log/{filename}')
    with open(f'log/{filename}', 'w', encoding='utf-8') as f:
        json_str = json.dumps(log, indent=0, ensure_ascii=False)
        f.write(json_str)
        f.write('\n')
    print('log saved in '+f'log/{filename}')
if __name__ == "__main__":
    history=[111]
    record(history)