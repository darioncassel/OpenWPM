
def visit(command_sequence):
    command_sequence.get(sleep=0, timeout=60)

def scroll(command_sequence):
    command_sequence.page_down(count=5)

def save_page_source(command_sequence):
    command_sequence.dump_page_source(suffix='__BY_GROUP', timeout=120)

def extract_topics(lines):
    topics = []
    for l in lines:
        if "- Topic" in l:
            topic_str = l.split("- Topic")[0][-20:]
            if ">" in topic_str:
                topic = topic_str.split(">")[-1]
                topics.append(topic.strip())
            elif "\"" in topic_str:
                topic = topic_str.split("\"")[-1]
                topics.append(topic.strip())
    return list(set(topics))

def normalized_difference(m1, m2):
    num_rows = min(len(m1), len(m2))
    num_cols = min(len(m1[0]), len(m2[0]))
    diff = 0.0
    for i in range(num_rows):
        for j in range(num_cols):
            diff += abs(m1[i][j] - m2[i][j])
    return diff / (num_rows * num_cols)

def test_statistic(observed_values, unit_assignments):
    norm_diff = 0
    for block_num, block in enumerate(observed_values):
        m1 = []
        m2 = []
        for browser_id, data in enumerate(block):
            if unit_assignments[block_num][browser_id]:
                m1.append(data)
            else:
                m2.append(data)
        norm_diff += normalized_difference(m1, m2)
    return norm_diff
