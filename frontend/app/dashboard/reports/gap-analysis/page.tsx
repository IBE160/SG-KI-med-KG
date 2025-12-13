"use client";

import * as React from "react";
import { RoleGuard } from "@/lib/role";
import { useRegulatoryFrameworks } from "@/hooks/useMappings";
import { useGapAnalysisReport } from "@/hooks/useGapAnalysis";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Printer } from "lucide-react";

export default function GapAnalysisPage() {
  const [selectedFrameworkId, setSelectedFrameworkId] = React.useState<string>("");

  const {
    data: frameworks,
    isLoading: frameworksLoading,
  } = useRegulatoryFrameworks();

  const {
    data: report,
    isLoading: reportLoading,
    error: reportError,
  } = useGapAnalysisReport(selectedFrameworkId);

  const handlePrint = () => {
    window.print();
  };

  return (
    <RoleGuard allowedRoles={["admin", "executive"]}>
      <div className="p-8 max-w-7xl mx-auto space-y-6 print:p-0 print:max-w-none">
        <div className="flex justify-between items-start print:hidden">
          <div>
            <h1 className="text-3xl font-bold mb-2">Gap Analysis Report</h1>
            <p className="text-muted-foreground">
              Identify compliance gaps for regulatory frameworks
            </p>
          </div>
          {report && (
            <Button onClick={handlePrint} variant="outline">
              <Printer className="mr-2 h-4 w-4" />
              Print Report
            </Button>
          )}
        </div>

        {/* Framework Selector - Hidden when printing */}
        <Card className="print:hidden">
          <CardHeader>
            <CardTitle className="text-lg">Select Framework</CardTitle>
          </CardHeader>
          <CardContent>
            {frameworksLoading ? (
              <Skeleton className="h-10 w-full" />
            ) : (
              <Select
                value={selectedFrameworkId}
                onValueChange={setSelectedFrameworkId}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a regulatory framework..." />
                </SelectTrigger>
                <SelectContent>
                  {frameworks?.items?.map((fw: { id: string; name: string }) => (
                    <SelectItem key={fw.id} value={fw.id}>
                      {fw.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </CardContent>
        </Card>

        {/* Report Content */}
        {selectedFrameworkId && (
          <div className="space-y-6">
            {reportLoading ? (
              <div className="space-y-4">
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-64 w-full" />
              </div>
            ) : report ? (
              <>
                {/* Print Header */}
                <div className="hidden print:block mb-8">
                  <h1 className="text-2xl font-bold">{report.framework_name}</h1>
                  <p className="text-gray-500">Gap Analysis Report</p>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium">
                        Total Requirements
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {report.total_requirements}
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium">
                        Mapped
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-green-600">
                        {report.mapped_requirements}
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium">
                        Unmapped (Gaps)
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-red-600">
                        {report.unmapped_requirements}
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium">
                        Coverage
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {report.coverage_percentage.toFixed(1)}%
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Unmapped Requirements Table */}
                <Card>
                  <CardHeader>
                    <CardTitle>Unmapped Requirements</CardTitle>
                    <CardDescription>
                      The following requirements have no associated controls.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {report.gaps.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        No gaps found! 100% coverage.
                      </div>
                    ) : (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Requirement Name</TableHead>
                            <TableHead>Description</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {report.gaps.map((gap: { requirement_id: string; requirement_name: string; requirement_description: string }) => (
                            <TableRow key={gap.requirement_id}>
                              <TableCell className="font-medium">
                                {gap.requirement_name}
                              </TableCell>
                              <TableCell>{gap.requirement_description}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    )}
                  </CardContent>
                </Card>
              </>
            ) : reportError ? (
               <div className="text-center text-red-500 py-8">
                 Failed to load report. Please try again.
               </div>
            ) : null}
          </div>
        )}
      </div>
    </RoleGuard>
  );
}
