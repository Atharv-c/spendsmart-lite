from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from .models import Expense
from .forms import ExpenseForm


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    category = request.GET.get('category')
    if category:
        expenses = expenses.filter(category=category)

    total = expenses.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'dashboard.html', {
        'expenses': expenses,
        'total': total,
        'categories': Expense.CATEGORY_CHOICES,
        'selected_category': category or '',
    })


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()

    return render(request, 'expense_form.html', {
        'form': form,
        'page_title': 'Add Expense',
    })


@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(
        Expense,
        id=expense_id,
        user=request.user
    )

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expense_form.html', {
        'form': form,
        'page_title': 'Edit Expense',
    })


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(
        Expense,
        id=expense_id,
        user=request.user
    )

    if request.method == 'POST':
        expense.delete()
        return redirect('dashboard')

    return render(request, 'confirm_delete.html', {
        'expense': expense,
    })