from faker import Faker
import random
import graph_logic

def generate_profiles():
    fake = Faker()
    roles_list = ['Developer','Mentor','Investor','Designer','Analyst','Researcher','Advisor','Entrepreneur']
    PROFILES = {}
    # Create 'me'
    PROFILES['me'] = {
        'id': 'me',
        'name': fake.name(),
        'roles': ['Developer', 'Mentor'],
        'bio_short': fake.sentence(nb_words=8),
        'bio_long': fake.paragraph(nb_sentences=3),
        'looking_for': fake.sentence(nb_words=6),
        'offering': fake.sentence(nb_words=6),
        'telegram': fake.user_name(),
        'avatarUrl': f'https://i.pravatar.cc/150?u=me',
        'contacts': []
    }
    graph_logic.add_user('me', name=PROFILES['me']['name'], roles=PROFILES['me']['roles'], phoneHash=fake.md5())
    # Personal contacts (degree 1)
    personal_ids = [f'u{i}' for i in range(1, 11)]
    for pid in personal_ids:
        name = fake.name()
        roles = random.sample(roles_list, k=random.randint(1, 3))
        PROFILES[pid] = {
            'id': pid,
            'name': name,
            'roles': roles,
            'bio_short': fake.sentence(nb_words=8),
            'bio_long': fake.paragraph(nb_sentences=3),
            'looking_for': fake.sentence(nb_words=6),
            'offering': fake.sentence(nb_words=6),
            'telegram': fake.user_name(),
            'avatarUrl': f'https://i.pravatar.cc/150?u={pid}',
            'contacts': ['me']
        }
        graph_logic.add_user(pid, name=name, roles=roles, phoneHash=fake.md5())
        graph_logic.add_relationship('me', pid, weight=round(random.uniform(1.0, 5.0), 2), status='connected')
        PROFILES['me']['contacts'].append(pid)
    # Friends of friends
    friend2_ids = [f'u{i}' for i in range(11, 26)]
    friend3_ids = [f'u{i}' for i in range(26, 41)]
    friend4_ids = [f'u{i}' for i in range(41, 51)]
    # degree 2
    for fid in friend2_ids:
        name = fake.name()
        roles = random.sample(roles_list, k=random.randint(1, 3))
        connect_to = random.choice(personal_ids)
        PROFILES[fid] = {
            'id': fid,
            'name': name,
            'roles': roles,
            'bio_short': fake.sentence(nb_words=8),
            'bio_long': fake.paragraph(nb_sentences=3),
            'looking_for': fake.sentence(nb_words=6),
            'offering': fake.sentence(nb_words=6),
            'telegram': fake.user_name(),
            'avatarUrl': f'https://i.pravatar.cc/150?u={fid}',
            'contacts': [connect_to]
        }
        graph_logic.add_user(fid, name=name, roles=roles, phoneHash=fake.md5())
        graph_logic.add_relationship(fid, connect_to, weight=round(random.uniform(1.0, 5.0), 2), status='connected')
        PROFILES[connect_to]['contacts'].append(fid)
    # degree 3
    for fid in friend3_ids:
        name = fake.name()
        roles = random.sample(roles_list, k=random.randint(1, 3))
        connect_to = random.choice(friend2_ids)
        PROFILES[fid] = {
            'id': fid,
            'name': name,
            'roles': roles,
            'bio_short': fake.sentence(nb_words=8),
            'bio_long': fake.paragraph(nb_sentences=3),
            'looking_for': fake.sentence(nb_words=6),
            'offering': fake.sentence(nb_words=6),
            'telegram': fake.user_name(),
            'avatarUrl': f'https://i.pravatar.cc/150?u={fid}',
            'contacts': [connect_to]
        }
        graph_logic.add_user(fid, name=name, roles=roles, phoneHash=fake.md5())
        graph_logic.add_relationship(fid, connect_to, weight=round(random.uniform(1.0, 5.0), 2), status='connected')
        PROFILES[connect_to]['contacts'].append(fid)
    # degree 4
    for fid in friend4_ids:
        name = fake.name()
        roles = random.sample(roles_list, k=random.randint(1, 3))
        connect_to = random.choice(friend3_ids)
        PROFILES[fid] = {
            'id': fid,
            'name': name,
            'roles': roles,
            'bio_short': fake.sentence(nb_words=8),
            'bio_long': fake.paragraph(nb_sentences=3),
            'looking_for': fake.sentence(nb_words=6),
            'offering': fake.sentence(nb_words=6),
            'telegram': fake.user_name(),
            'avatarUrl': f'https://i.pravatar.cc/150?u={fid}',
            'contacts': [connect_to]
        }
        graph_logic.add_user(fid, name=name, roles=roles, phoneHash=fake.md5())
        graph_logic.add_relationship(fid, connect_to, weight=round(random.uniform(1.0, 5.0), 2), status='connected')
        PROFILES[connect_to]['contacts'].append(fid)
    return PROFILES