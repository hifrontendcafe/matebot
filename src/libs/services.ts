import { AWS_API_KEY, AWS_URL } from "./environment.js";

const AWS_HEADERS = { "x-api-key": AWS_API_KEY };

export async function patchWarning({
  authorId,
  authorUsername,
  forgiveCause,
  menteeId,
}: {
  authorId: string;
  authorUsername: string;
  forgiveCause: string | null;
  menteeId: string;
}) {
  throw Error("// TODO: Delete me.");
  const response = await fetch(`${AWS_URL}/warning/mentee/${menteeId}`, {
    method: "PATCH",
    headers: AWS_HEADERS,
    body: JSON.stringify({
      forgive_cause: forgiveCause ? forgiveCause : "Sin motivo",
      forgive_author_id: authorId,
      forgive_author_username_discord: authorUsername,
    }),
  });

  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }

  return await response.json();
}

export async function postWarning({
  authorId,
  authorUsername,
  menteeId,
  menteeUsername,
  warnCause,
}: {
  authorId: string;
  authorUsername: string;
  menteeId: string;
  menteeUsername: string;
  warnCause: string | null;
}) {
  throw Error("// TODO: Delete me.");
  const response = await fetch(`${AWS_URL}/matebot/warning`, {
    method: "POST",
    headers: AWS_HEADERS,
    body: JSON.stringify({
      mentee_id: menteeId,
      mentee_username_discord: menteeUsername,
      warning_author_id: authorId,
      warning_author_username_discord: authorUsername,
      warn_cause: warnCause ? warnCause : "Ausencia a la mentoría",
      warn_type: warnCause ? "COC_WARN" : "NO_ASSIST",
    }),
  });

  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }

  return await response.json();
}

export async function postMentorship({
  authorId,
  authorUsername,
  menteeId,
  menteeUsername,
}: {
  authorId: string;
  authorUsername: string;
  menteeId: string;
  menteeUsername: string;
}) {
  throw Error("// TODO: Delete me.");
  const response = await fetch(`${AWS_URL}/matebot/mentorship`, {
    method: "POST",
    headers: AWS_HEADERS,
    body: JSON.stringify({
      mentor_id: authorId,
      mentor_username_discord: authorUsername,
      mentee_id: menteeId,
      mentee_username_discord: menteeUsername,
    }),
  });

  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }

  return await response.json();
}
