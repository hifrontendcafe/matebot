import fauna from "faunadb";
import { FAUNADB_SECRET_KEY } from "../libs/environment.js";

export const client = new fauna.Client({
  secret: FAUNADB_SECRET_KEY,
});

export const query = fauna.query;

// Types
export type Ref = fauna.Expr;
