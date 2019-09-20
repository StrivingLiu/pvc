# ******* WARNING - AUTO GENERATED CODE - DO NOT EDIT *******
from .VmomiSupport import CreateDataType, CreateManagedType
from .VmomiSupport import CreateEnumType
from .VmomiSupport import AddVersion, AddVersionParent
from .VmomiSupport import AddBreakingChangesInfo
from .VmomiSupport import F_LINK, F_LINKABLE
from .VmomiSupport import F_OPTIONAL, F_SECRET
from .VmomiSupport import newestVersions, stableVersions
from .VmomiSupport import publicVersions, dottedVersions
from .VmomiSupport import oldestVersions

AddVersion("vmodl.version.version0", "", "", 0, "vim25")
AddVersion("vmodl.version.version1", "", "", 0, "vim25")
AddVersion("cis.metadata.version.version1", "cis.metadata", "1.0", 0, "")
AddVersionParent("vmodl.version.version0", "vmodl.version.version0")
AddVersionParent("vmodl.version.version1", "vmodl.version.version0")
AddVersionParent("vmodl.version.version1", "vmodl.version.version1")
AddVersionParent("cis.metadata.version.version1", "vmodl.version.version0")
AddVersionParent("cis.metadata.version.version1", "vmodl.version.version1")
AddVersionParent("cis.metadata.version.version1", "cis.metadata.version.version1")

newestVersions.Add("cis.metadata.version.version1")
stableVersions.Add("cis.metadata.version.version1")
publicVersions.Add("cis.metadata.version.version1")
dottedVersions.Add("cis.metadata.version.version1")
oldestVersions.Add("cis.metadata.version.version1")

CreateDataType("cis.metadata.Descriptor", "CisMetadataDescriptor", "vmodl.DynamicData", "cis.metadata.version.version1", [("name", "string", "cis.metadata.version.version1", 0), ("title", "string", "cis.metadata.version.version1", 0), ("description", "string", "cis.metadata.version.version1", F_OPTIONAL), ("options", "vmodl.KeyAnyValue[]", "cis.metadata.version.version1", F_OPTIONAL)])
CreateDataType("cis.metadata.MemberDescriptor", "CisMetadataMemberDescriptor", "cis.metadata.Descriptor", "cis.metadata.version.version1", [("unit", "string", "cis.metadata.version.version1", F_OPTIONAL), ("type", "cis.metadata.TypeDescriptor", "cis.metadata.version.version1", 0), ("staticValueSpace", "cis.metadata.XSFacet[]", "cis.metadata.version.version1", F_OPTIONAL), ("optional", "boolean", "cis.metadata.version.version1", F_OPTIONAL), ("defaultValue", "anyType", "cis.metadata.version.version1", F_OPTIONAL)])
CreateEnumType("cis.metadata.MemberDescriptor.FrequencyUnit", "CisMetadataMemberDescriptorFrequencyUnit", "cis.metadata.version.version1", ["HZ", "KHZ", "MHZ", "GHZ"])
CreateEnumType("cis.metadata.MemberDescriptor.DateUnit", "CisMetadataMemberDescriptorDateUnit", "cis.metadata.version.version1", ["DATE", "TIME", "DATETIME"])
CreateEnumType("cis.metadata.MemberDescriptor.BitRateUnit", "CisMetadataMemberDescriptorBitRateUnit", "cis.metadata.version.version1", ["BPS", "KBPS", "MBPS", "GBPS"])
CreateEnumType("cis.metadata.MemberDescriptor.TimeSpanUnit", "CisMetadataMemberDescriptorTimeSpanUnit", "cis.metadata.version.version1", ["MILLISECONDS", "SECONDS", "MINUTES", "HOURS", "DAYS"])
CreateEnumType("cis.metadata.MemberDescriptor.DataSizeUnit", "CisMetadataMemberDescriptorDataSizeUnit", "cis.metadata.version.version1", ["BYTE", "KB", "MB", "GB", "TB"])
CreateDataType("cis.metadata.PropertyDescriptor", "CisMetadataPropertyDescriptor", "cis.metadata.MemberDescriptor", "cis.metadata.version.version1", [("immutable", "boolean", "cis.metadata.version.version1", F_OPTIONAL)])
CreateDataType("cis.metadata.TypeDescriptor", "CisMetadataTypeDescriptor", "cis.metadata.Descriptor", "cis.metadata.version.version1", [("immutable", "boolean", "cis.metadata.version.version1", F_OPTIONAL), ("properties", "cis.metadata.PropertyDescriptor[]", "cis.metadata.version.version1", F_OPTIONAL)])
CreateDataType("cis.metadata.XSFacet", "CisMetadataXSFacet", "vmodl.DynamicData", "cis.metadata.version.version1", [("type", "cis.metadata.XSFacetType", "cis.metadata.version.version1", 0), ("value", "anyType", "cis.metadata.version.version1", 0)])
CreateDataType("cis.metadata.XSFacetType", "CisMetadataXSFacetType", "vmodl.DynamicData", "cis.metadata.version.version1", [("choice", "string", "cis.metadata.version.version1", 0)])
CreateEnumType("cis.metadata.XSFacetType.XSFacetTypeChoice", "CisMetadataXSFacetTypeXSFacetTypeChoice", "cis.metadata.version.version1", ["PATTERN", "ENUMERATION", "LENGTH", "MINLENGTH", "MAXLENGTH", "TOTALDIGITS", "FRACTIONDIGITS", "MININCLUSIVE", "MAXINCLUSIVE", "MINEXCLUSIVE", "MAXEXCLUSIVE", "WHITESPACE"])
