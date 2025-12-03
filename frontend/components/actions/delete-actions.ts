"use server";

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import {
  deleteControl,
  deleteRisk,
  deleteBusinessProcess,
  deleteRegulatoryFramework,
} from "@/app/clientService";

export async function removeControl(id: string) {
  try {
    const cookieStore = cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      throw new Error("Authentication token not found");
    }

    await deleteControl({
      headers: { Authorization: `Bearer ${token}` },
      path: { control_id: id },
    });
    revalidatePath("/dashboard/controls");
  } catch (error) {
    console.error("Failed to delete control:", error);
    throw error;
  }
}

export async function removeRisk(id: string) {
  try {
    const cookieStore = cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      throw new Error("Authentication token not found");
    }

    await deleteRisk({
      headers: { Authorization: `Bearer ${token}` },
      path: { risk_id: id },
    });
    revalidatePath("/dashboard/risks");
  } catch (error) {
    console.error("Failed to delete risk:", error);
    throw error;
  }
}

export async function removeBusinessProcess(id: string) {
  try {
    const cookieStore = cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      throw new Error("Authentication token not found");
    }

    await deleteBusinessProcess({
      headers: { Authorization: `Bearer ${token}` },
      path: { process_id: id },
    });
    revalidatePath("/dashboard/business-processes");
  } catch (error) {
    console.error("Failed to delete business process:", error);
    throw error;
  }
}

export async function removeRegulatoryFramework(id: string) {
  try {
    const cookieStore = cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      throw new Error("Authentication token not found");
    }

    await deleteRegulatoryFramework({
      headers: { Authorization: `Bearer ${token}` },
      path: { framework_id: id },
    });
    revalidatePath("/dashboard/regulatory-frameworks");
  } catch (error) {
    console.error("Failed to delete regulatory framework:", error);
    throw error;
  }
}
