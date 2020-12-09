import random
import itertools
from flaskr.db import get_db

def hobby_of_users_create(participant):
  db = get_db()

  hobbys = db.execute(
    'SELECT category'
    ' FROM hobby'
    ' WHERE user_id = ?',
    (participant['user_id'],)
  ).fetchall()

  return hobbys

def hobby_search(hobbys_of_user1, hobbys_of_user2):
  match_number = 0

  for hobby1 in hobbys_of_user1:
    for hobby2 in hobbys_of_user2:
      if hobby1['category'] == hobby2['category']:
        match_number += 1
        break

  return match_number

def hobby_divide_sort_list(participants_list):
  search_list = []
  divide_sort_list = []

  for i, user1 in enumerate(participants_list):
    for user2 in participants_list[i + 1:]:
      match_num = hobby_search(hobby_of_users_create(user1), hobby_of_users_create(user2))

      search_list.append(user1['user_id'])
      search_list.append(user2['user_id'])
      search_list.append(match_num)
      divide_sort_list.append(search_list)

      search_list = []

  divide_sort_list.sort(key=lambda x: x[2], reverse=True)

  return divide_sort_list

def hobby_score_number(participants_order, divide_list):
  score = 0

  for i in range(len(participants_order) - 2):
    for j in range(1, 3):
      for divide in divide_list:
        next_to_order = [participants_order[i]['user_id'], participants_order[i + j]['user_id']]
        if next_to_order == divide[:-1]:
          score += divide[2] * j

  last_next_order = [participants_order[-2]['user_id'], participants_order[-1]['user_id']]
  for divide in divide_list:
    if last_next_order == divide[:-1]:
      score += divide[2]

  return score

def hobby_high_score_index(score_list):
  index_list = []
  high_score_list = sorted(score_list, reverse=True)

  for i, score in enumerate(score_list):
    for high_score in high_score_list[:3]:
      if high_score == score:
        index_list.append(i)
        break

  return index_list

def hobby_high_score_list(participants_list, divide_list):
  all_pattern_list = list(itertools.permutations(participants_list))
  score_list = []
  high_score_list = []

  for one_pattern_order in all_pattern_list:
    score_list.append(hobby_score_number(one_pattern_order, divide_list))

  for index in hobby_high_score_index(score_list):
    high_score_list.append(all_pattern_list[index])

  return high_score_list

def hobby_seat_change(participants_list):
  divide_list = hobby_divide_sort_list(participants_list)
  seat_result = hobby_high_score_list(participants_list, divide_list)
  random.shuffle(seat_result)

  return list(seat_result[0])

def common_shuffle_list(divide_list):
  order_list = []

  for one_list in divide_list:
    random.shuffle(one_list)

    for one_id in one_list:
      order_list.append(one_id)

  return order_list

def common_change_object_list(id_list, participants_list):
  object_list = []

  for list_id in id_list:
    for participant in participants_list:
      if list_id == participant['user_id']:
        object_list.append(participant)
        break

  return object_list

def common_change_object_divide_list(divide_list, participants_list):
  for i, one_list in enumerate(divide_list):
    object_list = common_change_object_list(one_list, participants_list)
    divide_list[i] = object_list

  return divide_list

def common_link_list(divide_list):
  order_list = []

  for one_list in divide_list:
    for one_id in one_list:
      order_list.append(one_id)

  return order_list

def smoke_alcohol_shuffle_list(participants_list, divide_list, hobby_check):
  order_list = []

  if hobby_check == 1:

  else:
    id_order_list = common_shuffle_list(divide_list)
    seat_result = common_change_object_list(id_order_list, participants_list)

  return seat_result

def smoke_create_user_list(participants_list):
  db = get_db()

  smoke_list = []

  for participant in participants_list:
    smoke = db.execute(
      'SELECT user_id, degree'
      ' FROM smoke'
      ' WHERE user_id = ?',
      (participant['user_id'],)
    ).fetchone()

    smoke_list.append(smoke)

  return smoke_list

def smoke_divide_list(participants_list):
  smoke_list = smoke_create_user_list(participants_list)
  divide_list = [[] for i in range(3)]

  for smoke in smoke_list:
    if smoke['degree'] == "吸う":
      divide_list[0].append(smoke['user_id'])
    elif smoke['degree'] == "吸わない":
      divide_list[1].append(smoke['user_id'])
    elif smoke['degree'] == "無理":
      divide_list[2].append(smoke['user_id'])

  return divide_list

def smoke_seat_change(participants_list, hobby_check):
  divide_list = smoke_divide_list(participants_list)
  seat_result = smoke_alcohol_shuffle_list(participants_list, divide_list, hobby_check)

  return seat_result

def alcohol_create_user_list(participants_list):
  db = get_db()
  alcohol_list = []

  for participant in participants_list:
    alcohol = db.execute(
      'SELECT user_id, degree'
      ' FROM alcohol'
      ' WHERE user_id = ?',
      (participant['user_id'],)
    ).fetchone()

    alcohol_list.append(alcohol)

  return alcohol_list

def alcohol_divide_list(participants_list):
  alcohol_list = alcohol_create_user_list(participants_list)
  divide_list = [[] for i in range(4)]

  for alcohol in alcohol_list:
    if alcohol['degree'] == "たくさん飲む":
      divide_list[0].append(alcohol['user_id'])
    elif alcohol['degree'] == "普通":
      divide_list[1].append(alcohol['user_id'])
    elif alcohol['degree'] == "あまり飲まない":
      divide_list[2].append(alcohol['user_id'])
    elif alcohol['degree'] == "全く飲まない":
      divide_list[3].append(alcohol['user_id'])

  return divide_list

def alcohol_seat_change(participants_list):
  divide_list = alcohol_divide_list(participants_list)
  seat_result = smoke_alcohol_shuffle_list(participants_list, divide_list, hobby_check)

  return seat_result

def smoke_and_alcohol_create_user_list(participants_list):
  db = get_db()

  smoke_list = smoke_create_user_list(participants_list)
  alcohol_list = alcohol_create_user_list(participants_list)

  smoke_and_alcohol_user_list = zip(smoke_list, alcohol_list)

  return smoke_and_alcohol_user_list

def smoke_and_alcohol_divide_list(participants_list):
  user_list = smoke_and_alcohol_create_user_list(participants_list)
  divide_list = [[] for i in range(6)]
  smoke_degree = ["吸う", "吸わない", "無理"]
  alcohol_degree = ["たくさん飲む", "普通", "あまり飲まない", "全く飲まない"]

  for user in user_list:
    if user[1]['degree'] == alcohol_degree[2] or user[1]['degree'] == alcohol_degree[3]:
      if user[0]['degree'] == smoke_degree[2]:
        divide_list[0].append(user[0]['user_id'])
      elif user[0]['degree'] == smoke_degree[1]:
        divide_list[1].append(user[0]['user_id'])
      elif user[0]['degree'] == smoke_degree[0]:
        divide_list[5].append(user[0]['user_id'])
    elif user[1]['degree'] == alcohol_degree[0] or user[1]['degree'] == alcohol_degree[1]:
      if user[0]['degree'] == smoke_degree[2]:
        divide_list[2].append(user[0]['user_id'])
      elif user[0]['degree'] == smoke_degree[1]:
        divide_list[3].append(user[0]['user_id'])
      elif user[0]['degree'] == smoke_degree[0]:
        divide_list[4].append(user[0]['user_id'])

  return divide_list

def smoke_and_alcohol_seat_change(participants_list):
  divide_list = smoke_and_alcohol_divide_list(participants_list)
  seat_result = smoke_alcohol_shuffle_list(participants_list, divide_list, hobby_check)

  return seat_result

def gender_create_user_list(participants_list):
  db = get_db()

  gender_list = []

  for participant in participants_list:
    gender = db.execute(
      'SELECT id, gender'
      ' FROM user'
      ' WHERE id = ?',
      (participant['user_id'],)
    ).fetchone()

    gender_list.append(gender)

  return gender_list

def by_gender_shuffle_list(participants_list, divide_list, smoke_alcohol_check, hobby_check):
  if smoke_alcohol_check[0] == 1 and smoke_alcohol_check[1] == 1:
    divide_list = common_change_object_divide_list(divide_list, participant_list)

    for i, one_list in enumerate(divide_list):
      one_list = smoke_and_alcohol_seat_change(one_list)
      divide_list[i] = one_list

    seat_result = common_link_list(divide_list)

  elif smoke_alcohol_check[0] == 1:
    divide_list = common_change_object_divide_list(divide_list, participant_list)

    for i, one_list in enumerate(divide_list):
      one_list = smoke_seat_change(one_list)
      divide_list[i] = one_list

    seat_result = common_link_list(divide_list)

  elif smoke_alcohol_check[1] == 1:
    divide_list = common_change_object_divide_list(divide_list, participant_list)

    for i, one_list in enumerate(divide_list):
      one_list = alcohol_seat_change(one_list)
      divide_list[i] = one_list

    seat_result = common_link_list(divide_list)

  else:
    id_order_list = common_shuffle_list(divide_list)
    seat_result = common_change_object_list(id_order_list, participants_list)

  return seat_result

def by_gender_divide_list(participants_list):
  by_gender_list = gender_create_user_list(participants_list)
  divide_list = [[] for i in range(2)]

  for by_gender in by_gender_list:
    if by_gender['gender'] == "男":
      divide_list[0].append(by_gender['id'])
    elif by_gender['gender'] == "女":
      divide_list[1].append(by_gender['id'])
    elif by_gender['gender'] == "その他":
      divide_list[random.randint(0, 1)].append(by_gender['id'])

  if random.randint(0, 1) == 1:
    divide_list[0], divide_list[1] = divide_list[1], divide_list[0]

  return divide_list

def by_gender_seat_change(participants_list, smoke_alcohol_check, hobby_check):
  divide_list = by_gender_divide_list(participants_list)
  by_gender_shuffle_list(participants_list, divide_list, smoke_alcohol_check, hobby_check)

  return seat_result

def min_list(list_1, list_2):
  if len(list_1) < len(list_2):
    return list_1
  else:
    return list_2

def alternate_gender_divide_list(participants_list):
  gender_list = gender_create_user_list(participants_list)
  divide_list = [[] for i in range(2)]
  other_list = []

  for gender in gender_list:
    if gender['gender'] == "男":
      divide_list[0].append(gender['id'])
    elif gender['gender'] == "女":
      divide_list[1].append(gender['id'])
    elif gender['gender'] == "その他":
      other_list.append(gender['id'])

  for other in other_list:
    min_list(divide_list[0], divide_list[1]).append(other)

  return divide_list

def alternate_gender_shuffle_list(participants_list, smoke_alcohol_check, hobby_check):
  divide_list = alternate_gender_divide_list(participants_list)
  divide_list = common_change_object_list(divide_list, participants_list)

  if smoke_alcohol_check[0] == 1 and smoke_alcohol_check[1] == 1:
    for i, one_list in enumerate(divide_list):
      one_list = smoke_and_alcohol_seat_change(one_list)
      divide_list[i] = one_list

  elif smoke_alcohol_check[0] == 1:
    for i, one_list in enumerate(divide_list):
      one_list = smoke_seat_change(one_list)
      divide_list[i] = one_list

  elif smoke_alcohol_check[1] == 1:
    for i, one_list in enumerate(divide_list):
      one_list = alcohol_seat_change(one_list)
      divide_list[i] = one_list

  else:
    for i, one_list in enumerate(divide_list):
      random.shuffle(one_list)
      one_list = common_change_object_list(one_list)
      divide_list[i] = one_list

  if len(divide_list[0]) < len(divide_list[1]):
    divide_list[0], divide_list[1] = divide_list[1], divide_list[0]

  return divide_list

def alternate_gender_place_random(divide_long_list, order_list, finish_num):
  for i in range(1, finish_num):
    order_list.insert(random.randint(0, len(order_list)), divide_long_list[i * (-1)])
  return order_list

def alternate_gender_adjust_list(divide_list, order_list, first_loop_num):
  if len(divide_list[1]) % 2 == 0:
    if len(divide_list[0]) == len(divide_list[1]):
      for j in range(2):
        order_list.append(divide_list[j][-1])
    else:
      for j in range(1, 3):
        order_list.append(divide_list[0][first_loop_num * 2 + j])

      order_list.append(divide_list[1][-1])

      if len(divide_list[0]) != len(divide_list[1]) + 1:
        finish_num = len(divide_list[0]) - len(divide_list[1])
        alternate_gender_place_random(divide_list[0], order_list, finish_num)

  elif len(divide_list[0]) != len(divide_list[1]):
    finish_num = len(divide_list[0]) - len(divide_list[1]) + 1
    alternate_gender_place_random(divide_list[0], order_list, finish_num)

  return order_list

def alternate_gender_order_list(divide_list):
  order_list = []
  order_list.append(divide_list[0][0])
  order_list.append(divide_list[1][0])
  first_loop_num = (len(divide_list[1]) - 1) // 2

  for i in range(first_loop_num):
    for j in range(2):
      for k in range(-1, 1):
        order_list.append(divide_list[j][(i + 1) * 2 + k])

  order_list = alternate_gender_adjust_list(divide_list, order_list, first_loop_num)

  return order_list

def alternate_gender_seat_change(participants_list, smoke_alcohol_check, hobby_check):
  divide_list = alternate_gender_shuffle_list(participants_list)

  if len(divide_list[1]) == 0:
    id_order_list = common_shuffle_list(divide_list)
    seat_result = common_change_object_list(id_order_list, participants_list)
  else:
    seat_result = alternate_gender_order_list(divide_list)

  return seat_result

def seat_change(participants_list, smoke_alcohol_check, hobby_check, gender_check):
  if gender_check == 1:
    seat_result = by_gender_seat_change(participants_list, smoke_alcohol_check, hobby_check)
  elif gender_check == 2:
    seat_result = alternate_gender_seat_change(participants_list, smoke_alcohol_check, hobby_check)
  else:
    if smoke_alcohol_check[0] == 1 and smoke_alcohol_check[1] == 1:
      smoke_and_alcohol_seat_change(participants_list, hobby_check)
    elif smoke_alcohol_check[0] == 1:
      smoke_seat_change(participants_list, hobby_check)
    elif smoke_alcohol_check[1] == 1:
      alcohol_seat_change(participants_list, hobby_check)
    else:
      if hobby_check == 1:
        seat_result = hobby_seat_change(participants_list)
      else:
        random.shuffle(participants_list)
        seat_result = participants_list

  return seat_result
