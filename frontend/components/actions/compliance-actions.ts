"use server";

import {
  controlSchema,
  riskSchema,
  businessProcessSchema,
  regulatoryFrameworkSchema,
} from "@/lib/definitions";
import {
  createControl,
  updateControl,
  createRisk,
  updateRisk,
  createBusinessProcess,
  updateBusinessProcess,
  createRegulatoryFramework,
  updateRegulatoryFramework,
} from "@/app/clientService";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";

// Define a common state type for form actions
export type FormState =
  | {
      errors?: {
        name?: string[];
        description?: string[];
        type?: string[];
        category?: string[];
        version?: string[];
      };
      message?: string;
    }
  | undefined;

// --- Controls ---

export async function addControl(state: FormState, formData: FormData) {
  const validatedFields = controlSchema.safeParse({
    name: formData.get("name"),
    description: formData.get("description"),
    type: formData.get("type"),
  });

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
    };
  }

  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("accessToken")?.value;

    if (!token) {
      return {
        message: "Authentication token not found",
      };
    }

    const { name, description, type } = validatedFields.data;

    await createControl({
      headers: { Authorization: `Bearer ${token}` },
      body: { name, description, type },
    });
  } catch (error: any) {
    return {
      message:
        error.response?.data?.detail ||
        "Failed to create control. Please try again.",
    };
  }

  redirect("/dashboard/controls");
}

export async function editControl(state: FormState, formData: FormData) {
  const id = formData.get("id") as string;
  const validatedFields = controlSchema.safeParse({
    name: formData.get("name"),
    description: formData.get("description"),
    type: formData.get("type"),
  });

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
    };
  }

  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("accessToken")?.value;

    if (!token) {
      return {
        message: "Authentication token not found",
      };
    }

    const { name, description, type } = validatedFields.data;

    await updateControl({
      headers: { Authorization: `Bearer ${token}` },
      path: { control_id: id },
      body: { name, description, type },
    });
  } catch (error: any) {
    return {
      message:
        error.response?.data?.detail ||
        "Failed to update control. Please try again.",
    };
  }

  redirect("/dashboard/controls");
}

// --- Risks ---

export async function addRisk(state: FormState, formData: FormData) {
  const validatedFields = riskSchema.safeParse({
    name: formData.get("name"),
    description: formData.get("description"),
    category: formData.get("category"),
  });

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
    };
  }

  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("accessToken")?.value;

    if (!token) {
      return {
        message: "Authentication token not found",
      };
    }

    const { name, description, category } = validatedFields.data;

    await createRisk({
      headers: { Authorization: `Bearer ${token}` },
      body: { name, description, category },
    });
  } catch (error: any) {
    return {
      message:
        error.response?.data?.detail ||
        "Failed to create risk. Please try again.",
    };
  }

  redirect("/dashboard/risks");
}

export async function editRisk(state: FormState, formData: FormData) {
  const id = formData.get("id") as string;
  const validatedFields = riskSchema.safeParse({
    name: formData.get("name"),
    description: formData.get("description"),
    category: formData.get("category"),
  });

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
    };
  }

  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("accessToken")?.value;

    if (!token) {
      return {
        message: "Authentication token not found",
      };
    }

    const { name, description, category } = validatedFields.data;

    await updateRisk({
      headers: { Authorization: `Bearer ${token}` },
      path: { risk_id: id },
      body: { name, description, category },
    });
  } catch (error: any) {
    return {
      message:
        error.response?.data?.detail ||
        "Failed to update risk. Please try again.",
    };
  }

  redirect("/dashboard/risks");
}

// --- Business Processes ---

export async function addBusinessProcess(state: FormState, formData: FormData) {
  const validatedFields = businessProcessSchema.safeParse({
    name: formData.get("name"),
    description: formData.get("description"),
  });

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
    };
  }

  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("accessToken")?.value;

    if (!token) {
      return {
        message: "Authentication token not found",
      };
    }

    const { name, description } = validatedFields.data;

    await createBusinessProcess({
      headers: { Authorization: `Bearer ${token}` },
      body: { name, description },
    });
  } catch (error: any) {
    return {
      message:
        error.response?.data?.detail ||
        "Failed to create business process. Please try again.",
    };
  }

  redirect("/dashboard/business-processes");
}

export async function editBusinessProcess(
  state: FormState,
  formData: FormData,
) {
  const id = formData.get("id") as string;
  const validatedFields = businessProcessSchema.safeParse({
    name: formData.get("name"),
    description: formData.get("description"),
  });

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
    };
  }

  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("accessToken")?.value;

    if (!token) {
      return {
        message: "Authentication token not found",
      };
    }

    const { name, description } = validatedFields.data;

    await updateBusinessProcess({
      headers: { Authorization: `Bearer ${token}` },
      path: { process_id: id },
      body: { name, description },
    });
  } catch (error: any) {
    return {
      message:
        error.response?.data?.detail ||
        "Failed to update business process. Please try again.",
    };
  }

  redirect("/dashboard/business-processes");
}

// --- Regulatory Frameworks ---

export async function addRegulatoryFramework(
  state: FormState,
  formData: FormData,
) {
  const validatedFields = regulatoryFrameworkSchema.safeParse({
    name: formData.get("name"),
    description: formData.get("description"),
    version: formData.get("version"),
  });

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
    };
  }

  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("accessToken")?.value;

    if (!token) {
      return {
        message: "Authentication token not found",
      };
    }

    const { name, description, version } = validatedFields.data;

    await createRegulatoryFramework({
      headers: { Authorization: `Bearer ${token}` },
      body: { name, description, version },
    });
  } catch (error: any) {
    return {
      message:
        error.response?.data?.detail ||
        "Failed to create regulatory framework. Please try again.",
    };
  }

  redirect("/dashboard/regulatory-frameworks");
}

export async function editRegulatoryFramework(
  state: FormState,
  formData: FormData,
) {
  const id = formData.get("id") as string;
  const validatedFields = regulatoryFrameworkSchema.safeParse({
    name: formData.get("name"),
    description: formData.get("description"),
    version: formData.get("version"),
  });

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
    };
  }

  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("accessToken")?.value;

    if (!token) {
      return {
        message: "Authentication token not found",
      };
    }

    const { name, description, version } = validatedFields.data;

    await updateRegulatoryFramework({
      headers: { Authorization: `Bearer ${token}` },
      path: { framework_id: id },
      body: { name, description, version },
    });
  } catch (error: any) {
    return {
      message:
        error.response?.data?.detail ||
        "Failed to update regulatory framework. Please try again.",
    };
  }

  redirect("/dashboard/regulatory-frameworks");
}
