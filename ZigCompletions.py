import sublime
import sublime_plugin
import re
import os
import platform
import glob
import fnmatch
import time


class ZigCompletions(sublime_plugin.EventListener):
  built_in_procs = [
    ['@addWithOverflow(${1:comptime T: type}, ${2:a: T}, ${3:b: T}, ${4:result: *T})\tBuilt-in', '@addWithOverflow(comptime T: type, a: T, b: T, result: *T) bool'],
    ['@alignCast(${1:comptime alignment: u29}, ${2:ptr: var})\tBuilt-in', '@alignCast(comptime alignment: u29, ptr: var) var'],
    ['@alignOf(${1:comptime T: type})\tBuilt-in', '@alignOf(comptime T: type) comptime_int'],
    ['@as(${1:comptime T: type}, ${2:expression})\tBuilt-in', '@as(comptime T: type, expression) T'],
    ['@asyncCall(${1:frame_buffer: []align(@alignOf(@Frame(anyAsyncFunction))) u8}, ${2:result_ptr}, ${3:function_ptr}, ${4:args: ...})\tBuilt-in', '@asyncCall(frame_buffer: []align(@alignOf(@Frame(anyAsyncFunction))) u8, result_ptr, function_ptr, args: ...) anyframe->T'],
    ['@atomicLoad(${1:comptime T: type}, ${2:ptr: *const T}, ${3:comptime ordering: builtin.AtomicOrder})\tBuilt-in', '@atomicLoad(comptime T: type, ptr: *const T, comptime ordering: builtin.AtomicOrder) T'],
    ['@atomicRmw(${1:comptime T: type}, ${2:ptr: *T}, ${3:comptime op: builtin.AtomicRmwOp}, ${4:operand: T}, ${5:comptime ordering: builtin.AtomicOrder})\tBuilt-in', '@atomicRmw(comptime T: type, ptr: *T, comptime op: builtin.AtomicRmwOp, operand: T, comptime ordering: builtin.AtomicOrder) T'],
    ['@atomicStore(${1:comptime T: type}, ${2:ptr: *T}, ${3:value: T}, ${4:comptime ordering: builtin.AtomicOrder})\tBuilt-in', '@atomicStore(comptime T: type, ptr: *T, value: T, comptime ordering: builtin.AtomicOrder) void'],
    ['@bitCast(${1:comptime DestType: type}, ${2:value: var})\tBuilt-in', '@bitCast(comptime DestType: type, value: var) DestType'],
    ['@bitOffsetOf(${1:comptime T: type}, ${2:comptime field_name: []const u8})\tBuilt-in', '@bitOffsetOf(comptime T: type, comptime field_name: []const u8) comptime_int'],
    ['@boolToInt(${1:value: bool})\tBuilt-in', '@boolToInt(value: bool) u1'],
    ['@bitSizeOf(${1:comptime T: type})\tBuilt-in', '@bitSizeOf(comptime T: type) comptime_int'],
    ['@breakpoint()\tBuilt-in', '@breakpoint()'],
    ['@mulAdd(${1:comptime T: type}, ${2:a: T}, ${3:b: T}, ${4:c: T})\tBuilt-in', '@mulAdd(comptime T: type, a: T, b: T, c: T) T'],
    ['@byteSwap(${1:comptime T: type}, ${2:operand: T})\tBuilt-in', '@byteSwap(comptime T: type, operand: T) T'],
    ['@bitReverse(${1:comptime T: type}, ${2:integer: T})\tBuilt-in', '@bitReverse(comptime T: type, integer: T) T'],
    ['@byteOffsetOf(${1:comptime T: type}, ${2:comptime field_name: []const u8})\tBuilt-in', '@byteOffsetOf(comptime T: type, comptime field_name: []const u8) comptime_int'],
    ['@call(${1:options: std.builtin.CallOptions}, ${2:function: var}, ${3:args: var})\tBuilt-in', '@call(options: std.builtin.CallOptions, function: var, args: var) var'],
    ['@cDefine(${1:comptime name: []u8}, ${2:value})\tBuilt-in', '@cDefine(comptime name: []u8, value)'],
    ['@cImport(${1:expression})\tBuilt-in', '@cImport(expression) type'],
    ['@cInclude(${1:comptime path: []u8})\tBuilt-in', '@cInclude(comptime path: []u8)'],
    ['@clz(${1:comptime T: type}, ${2:integer: T})\tBuilt-in', '@clz(comptime T: type, integer: T)'],
    ['@cmpxchgStrong(${1:comptime T: type}, ${2:ptr: *T}, ${3:expected_value: T}, ${4:new_value: T}, ${5:success_order: AtomicOrder}, ${6:fail_order: AtomicOrder})\tBuilt-in', '@cmpxchgStrong(comptime T: type, ptr: *T, expected_value: T, new_value: T, success_order: AtomicOrder, fail_order: AtomicOrder) ?T'],
    ['@cmpxchgWeak(${1:comptime T: type}, ${2:ptr: *T}, ${3:expected_value: T}, ${4:new_value: T}, ${5:success_order: AtomicOrder}, ${6:fail_order: AtomicOrder})\tBuilt-in', '@cmpxchgWeak(comptime T: type, ptr: *T, expected_value: T, new_value: T, success_order: AtomicOrder, fail_order: AtomicOrder) ?T'],
    ['@compileError(${1:comptime msg: []u8})\tBuilt-in', '@compileError(comptime msg: []u8)'],
    ['@compileLog(${1:args: ...})\tBuilt-in', '@compileLog(args: ...)'],
    ['@ctz(${1:comptime T: type}, ${2:integer: T})\tBuilt-in', '@ctz(comptime T: type, integer: T)'],
    ['@cUndef(${1:comptime name: []u8})\tBuilt-in', '@cUndef(comptime name: []u8)'],
    ['@divExact(${1:numerator: T}, ${2:denominator: T})\tBuilt-in', '@divExact(numerator: T, denominator: T) T'],
    ['@divFloor(${1:numerator: T}, ${2:denominator: T})\tBuilt-in', '@divFloor(numerator: T, denominator: T) T'],
    ['@divTrunc(${1:numerator: T}, ${2:denominator: T})\tBuilt-in', '@divTrunc(numerator: T, denominator: T) T'],
    ['@embedFile(${1:comptime path: []const u8})\tBuilt-in', '@embedFile(comptime path: []const u8) *const [X:0]u8'],
    ['@enumToInt(${1:enum_or_tagged_union: var})\tBuilt-in', '@enumToInt(enum_or_tagged_union: var) var'],
    ['@errorName(${1:err: anyerror})\tBuilt-in', '@errorName(err: anyerror) []const u8'],
    ['@errorReturnTrace()\tBuilt-in', '@errorReturnTrace() ?*builtin.StackTrace'],
    ['@errorToInt(${1:err: var) std.meta.IntType(false}, ${2:@sizeOf(anyerror})\tBuilt-in', '@errorToInt(err: var) std.meta.IntType(false, @sizeOf(anyerror) * 8)'],
    ['@errSetCast(${1:comptime T: DestType}, ${2:value: var})\tBuilt-in', '@errSetCast(comptime T: DestType, value: var) DestType'],
    ['@export(${1:target: var}, ${2:comptime options: std.builtin.ExportOptions})\tBuilt-in', '@export(target: var, comptime options: std.builtin.ExportOptions) void'],
    ['@fence(${1:order: AtomicOrder})\tBuilt-in', '@fence(order: AtomicOrder)'],
    ['@field(${1:lhs: var}, ${2:comptime field_name: []const u8})\tBuilt-in', '@field(lhs: var, comptime field_name: []const u8) (field)'],
    ['@fieldParentPtr(${1:comptime ParentType: type}, ${2:comptime field_name: []const u8}, ${3:field_ptr: *T})\tBuilt-in', '@fieldParentPtr(comptime ParentType: type, comptime field_name: []const u8,field_ptr: *T) *ParentType'],
    ['@floatCast(${1:comptime DestType: type}, ${2:value: var})\tBuilt-in', '@floatCast(comptime DestType: type, value: var) DestType'],
    ['@floatToInt(${1:comptime DestType: type}, ${2:float: var})\tBuilt-in', '@floatToInt(comptime DestType: type, float: var) DestType'],
    ['@frame()\tBuilt-in', '@frame() *@Frame(func)'],
    ['@Frame(${1:func: var})\tBuilt-in', '@Frame(func: var) type'],
    ['@frameAddress()\tBuilt-in', '@frameAddress() usize'],
    ['@frameSize()\tBuilt-in', '@frameSize() usize'],
    ['@hasDecl(${1:comptime Container: type}, ${2:comptime name: []const u8})\tBuilt-in', '@hasDecl(comptime Container: type, comptime name: []const u8) bool'],
    ['@hasField(${1:comptime Container: type}, ${2:comptime name: []const u8})\tBuilt-in', '@hasField(comptime Container: type, comptime name: []const u8) bool'],
    ['@import(${1:comptime path: []u8})\tBuilt-in', '@import(comptime path: []u8) type'],
    ['@intCast(${1:comptime DestType: type}, ${2:int: var})\tBuilt-in', '@intCast(comptime DestType: type, int: var) DestType'],
    ['@intToEnum(${1:comptime DestType: type}, ${2:int_value: @TagType(DestType)})\tBuilt-in', '@intToEnum(comptime DestType: type, int_value: @TagType(DestType)) DestType'],
    ['@intToError(${1:value: std.meta.IntType(false, @sizeOf(anyerror) * 8)})\tBuilt-in', '@intToError(value: std.meta.IntType(false, @sizeOf(anyerror) * 8)) anyerror'],
    ['@intToFloat(${1:comptime DestType: type}, ${2:int: var})\tBuilt-in', '@intToFloat(comptime DestType: type, int: var) DestType'],
    ['@intToPtr(${1:comptime DestType: type}, ${2:address: usize})\tBuilt-in', '@intToPtr(comptime DestType: type, address: usize) DestType'],
    ['@memcpy(${1:noalias dest: [*]u8}, ${2:noalias source: [*]const u8}, ${3:byte_count: usize})\tBuilt-in', '@memcpy(noalias dest: [*]u8, noalias source: [*]const u8, byte_count: usize)'],
    ['@memset(${1:dest: [*]u8}, ${2:c: u8}, ${3:byte_count: usize})\tBuilt-in', '@memset(dest: [*]u8, c: u8, byte_count: usize)'],
    ['@mod(${1:numerator: T}, ${2:denominator: T})\tBuilt-in', '@mod(numerator: T, denominator: T) T'],
    ['@mulWithOverflow(${1:comptime T: type}, ${2:a: T}, ${3:b: T}, ${4:result: *T})\tBuilt-in', '@mulWithOverflow(comptime T: type, a: T, b: T, result: *T) bool'],
    ['@OpaqueType()\tBuilt-in', '@OpaqueType() type'],
    ['@panic(${1:message: []const u8})\tBuilt-in', '@panic(message: []const u8) noreturn'],
    ['@popCount(${1:comptime T: type}, ${2:integer: T})\tBuilt-in', '@popCount(comptime T: type, integer: T)'],
    ['@ptrCast(${1:comptime DestType: type}, ${2:value: var})\tBuilt-in', '@ptrCast(comptime DestType: type, value: var) DestType'],
    ['@ptrToInt(${1:value: var})\tBuilt-in', '@ptrToInt(value: var) usize'],
    ['@rem(${1:numerator: T}, ${2:denominator: T})\tBuilt-in', '@rem(numerator: T, denominator: T) T'],
    ['@returnAddress()\tBuilt-in', '@returnAddress() usize'],
    ['@setAlignStack(${1:comptime alignment: u29})\tBuilt-in', '@setAlignStack(comptime alignment: u29)'],
    ['@setCold(${1:is_cold: bool})\tBuilt-in', '@setCold(is_cold: bool)'],
    ['@setEvalBranchQuota(${1:new_quota: usize})\tBuilt-in', '@setEvalBranchQuota(new_quota: usize)'],
    ['@setFloatMode(${1:mode: @import("builtin").FloatMode})\tBuilt-in', '@setFloatMode(mode: @import("builtin").FloatMode)'],
    ['@setRuntimeSafety(${1:safety_on: bool})\tBuilt-in', '@setRuntimeSafety(safety_on: bool)'],
    ['@shlExact(${1:value: T}, ${2:shift_amt: Log2T})\tBuilt-in', '@shlExact(value: T, shift_amt: Log2T) T'],
    ['@shlWithOverflow(${1:comptime T: type}, ${2:a: T}, ${3:shift_amt: Log2T}, ${4:result: *T})\tBuilt-in', '@shlWithOverflow(comptime T: type, a: T, shift_amt: Log2T, result: *T) bool'],
    ['@shrExact(${1:value: T}, ${2:shift_amt: Log2T})\tBuilt-in', '@shrExact(value: T, shift_amt: Log2T) T'],
    ['@shuffle(${1:comptime E: type}, ${2:a: @Vector(a_len, E)}, ${3:b: @Vector(b_len, E)}, ${4:comptime mask: @Vector(mask_len, i32)})\tBuilt-in', '@shuffle(comptime E: type, a: @Vector(a_len, E), b: @Vector(b_len, E), comptime mask: @Vector(mask_len, i32)) @Vector(mask_len, E)'],
    ['@sizeOf(${1:comptime T: type})\tBuilt-in', '@sizeOf(comptime T: type) comptime_int'],
    ['@splat(${1:comptime len: u32}, ${2:scalar: var})\tBuilt-in', '@splat(comptime len: u32, scalar: var) @Vector(len, @TypeOf(scalar))'],
    ['@sqrt(${1:value: var})\tBuilt-in', '@sqrt(value: var) @TypeOf(value)'],
    ['@sin(${1:value: var})\tBuilt-in', '@sin(value: var) @TypeOf(value)'],
    ['@cos(${1:value: var})\tBuilt-in', '@cos(value: var) @TypeOf(value)'],
    ['@exp(${1:value: var})\tBuilt-in', '@exp(value: var) @TypeOf(value)'],
    ['@exp2(${1:value: var})\tBuilt-in', '@exp2(value: var) @TypeOf(value)'],
    ['@log(${1:value: var})\tBuilt-in', '@log(value: var) @TypeOf(value)'],
    ['@log2(${1:value: var})\tBuilt-in', '@log2(value: var) @TypeOf(value)'],
    ['@log10(${1:value: var})\tBuilt-in', '@log10(value: var) @TypeOf(value)'],
    ['@fabs(${1:value: var})\tBuilt-in', '@fabs(value: var) @TypeOf(value)'],
    ['@floor(${1:value: var})\tBuilt-in', '@floor(value: var) @TypeOf(value)'],
    ['@ceil(${1:value: var})\tBuilt-in', '@ceil(value: var) @TypeOf(value)'],
    ['@trunc(${1:value: var})\tBuilt-in', '@trunc(value: var) @TypeOf(value)'],
    ['@round(${1:value: var})\tBuilt-in', '@round(value: var) @TypeOf(value)'],
    ['@subWithOverflow(${1:comptime T: type}, ${2:a: T}, ${3:b: T}, ${4:result: *T})\tBuilt-in', '@subWithOverflow(comptime T: type, a: T, b: T, result: *T) bool'],
    ['@tagName(${1:value: var})\tBuilt-in', '@tagName(value: var) []const u8'],
    ['@TagType(${1:T: type})\tBuilt-in', '@TagType(T: type) type'],
    ['@This()\tBuilt-in', '@This() type'],
    ['@truncate(${1:comptime T: type}, ${2:integer: var})\tBuilt-in', '@truncate(comptime T: type, integer: var) T'],
    ['@Type(${1:comptime info: @import("builtin").TypeInfo})\tBuilt-in', '@Type(comptime info: @import("builtin").TypeInfo) type'],
    ['@typeInfo(${1:comptime T: type})\tBuilt-in', '@typeInfo(comptime T: type) @import("std").builtin.TypeInfo'],
    ['@typeName(${1:T: type})\tBuilt-in', '@typeName(T: type) [N]u8'],
    ['@TypeOf(${1:...})\tBuilt-in', '@TypeOf(...) type'],
    ['@unionInit(${1:comptime Union: type}, ${2:comptime active_field_name: []const u8}, ${3:init_expr})\tBuilt-in', '@unionInit(comptime Union: type, comptime active_field_name: []const u8, init_expr) Union'],
    ['@Vector(${1:comptime len: u32}, ${2:comptime ElemType: type})\tBuilt-in', '@Vector(comptime len: u32, comptime ElemType: type) type'],
  ]

  # return True if all the previous chars are valid (a-zA-Z0-9_) up to the '.'
  def get_prefix_before_dot(self, file_view, loc):
    # next char should be some type of space, paren or non-word
    next_char = file_view.substr(sublime.Region(loc, loc + 1))
    if next_char.isalnum():
      return False

    # walk backwards until we find a '.'. If we hit a non-char (a-zA-Z0-9_) bail out since this isnt a completion
    curr_line_region = file_view.line(loc)

    def get_before_dot(dot_loc):
      region_end = dot_loc
      while dot_loc > curr_line_region.begin():
        prev_char = file_view.substr(sublime.Region(dot_loc - 1, dot_loc))
        if prev_char.isalnum() or prev_char == '_':
          dot_loc -= 1
        else:
          return file_view.substr(sublime.Region(dot_loc, region_end))
      return None

    while loc > curr_line_region.begin():
      char = file_view.substr(sublime.Region(loc - 1, loc))
      if char == '.':
        return get_before_dot(loc - 1)

      if char.isalnum() or char == '_':
        loc -= 1
      else:
        return None
    return None

  def on_query_completions(self, view, prefix, locations):
    if len(locations) > 1 or not view.file_name().endswith('.zig'):
      return None

    # cleanup before we start
    completions = []

    # dont bother with completions if we are in a comment block or string
    scope_name = view.scope_name(locations[0])
    no_completion_scopes = ['quoted.double', 'quoted.raw', 'comment.line', 'comment.block']
    if any(part in scope_name for part in no_completion_scopes):
      return None

    start_time = time.time()

    # extract the current text. If there is a '.' get the previous word to see if it matches a package
    file_view = sublime.active_window().find_open_file(view.file_name())
    curr_line_region = file_view.line(locations[0])
    curr_line = file_view.substr(curr_line_region).strip()

    # extract the string before the '.' in the current line if there is one and we are on the right side of it typing
    before_dot = self.get_prefix_before_dot(file_view, locations[0])

    # if we have no . in the text on the current line and it starts with '@' add the built-ins
    if before_dot == None:
      completions.extend(self.built_in_procs)

    #sort completions alphabetically
    if view.settings().get('zig_sort_completions_alphabetical', True):
      completions.sort()

    # Report time spent building completions before returning
    delta_time_ms = int((time.time() - start_time) * 1000)
    message = 'Zig autocompletion took ' + str(delta_time_ms) + 'ms. Completions: ' + str(len(completions))
    view.window().status_message(message)

    return completions


