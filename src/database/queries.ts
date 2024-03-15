import { FAUNADB_USER_COLLECTION_ID } from "../libs/environment.js";
import { Ref, client, query } from "./client.js";

type UserCollectionData = {
  new_users_id: string[];
  user_condition: number;
  time_sec: number;
  time_delta: number;
};

type GetUserList = {
  ref: Ref;
  ts: number;
  data: UserCollectionData;
};

export async function getUserList(): Promise<GetUserList> {
  return await client.query<GetUserList>(
    query.Get(query.Ref(query.Collection("Users"), FAUNADB_USER_COLLECTION_ID))
  );
}

export async function updateUserList(data: UserCollectionData) {
  return await client.query<GetUserList>(
    query.Update(query.Ref(query.Collection("Users"), FAUNADB_USER_COLLECTION_ID), {
      data,
    })
  );
}
